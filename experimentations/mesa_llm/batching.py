import asyncio
import logging
from typing import Any, Dict, List, Tuple


class ModuleLLM:
    _batch_processors: Dict[Tuple, "BatchProcessor"] = {}

    def __init__(
        self,
        provider: str,
        model_name: str,
        api_key: str,
        device: int = 0,
        max_batch: int = 16,
        flush_interval: float = 0.05,
        max_queue_size: int = 1000,
    ):
        # config that really matters for deduping
        self._config_key = (provider, model_name, device, api_key)
        self.provider = provider
        self.model_name = model_name
        self.api_key = api_key
        self.device = device

        # lazy‑loaded resources
        self._pipeline = None  # e.g. HF pipeline or OpenRouter client

        # batch processor is created once per unique config
        if self._config_key not in ModuleLLM._batch_processors:
            ModuleLLM._batch_processors[self._config_key] = BatchProcessor(
                client=self,
                max_batch=max_batch,
                flush_interval=flush_interval,
                max_queue_size=max_queue_size,
            )
        self._batch: BatchProcessor = ModuleLLM._batch_processors[self._config_key]

    # public API: async only
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a single completion via the shared batcher."""
        fut: asyncio.Future = asyncio.get_running_loop().create_future()
        await self._batch.enqueue(prompt, fut, kwargs)
        return await fut

    async def generate_batch(self, prompts: List[str], params: Dict[str, Any]) -> List[str]:
        """Direct batch call (used by the batcher)."""
        # lazy init
        if self._pipeline is None:
            self._pipeline = await self._init_pipeline()

        # could also be an option where provider is automatically selected based on the model name
        if self.provider == "huggingface":
            return await self._call_hf(prompts, params)
        elif self.provider == "openrouter":
            return await self._call_openrouter(prompts, params)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def _init_pipeline(self) -> Any:
        """Instantiate HF/OpenRouter client once."""
        # e.g. load transformers.pipeline or OpenAI client here
        ...

    async def _call_hf(self, prompts: List[str], params: Dict[str, Any]) -> List[str]:
        """HuggingFace batch inference."""
        ...

    async def _call_openrouter(self, prompts: List[str], params: Dict[str, Any]) -> List[str]:
        """OpenRouter (OpenAI/Claude/etc) batch API."""
        ...

    async def shutdown(self) -> None:
        """Gracefully shut down all batchers."""
        await asyncio.gather(*(bp.shutdown() for bp in ModuleLLM._batch_processors.values()))



class BatchProcessor:
    def __init__(
        self,
        client: ModuleLLM,
        max_batch: int,
        flush_interval: float,
        max_queue_size: int,
    ):
        self.client = client
        self.max_batch = max_batch
        self.flush_interval = flush_interval
        self.max_queue_size = max_queue_size

        # internal queue of (prompt, future, params)
        self._queue: List[Tuple[str, asyncio.Future, Dict[str, Any]]] = []
        self._lock = asyncio.Lock()
        self._flush_event = asyncio.Event()
        self._closed = False

        # start the flush loop
        self._task = asyncio.create_task(self._flush_loop())

    async def enqueue(
        self,
        prompt: str,
        fut: asyncio.Future,
        params: Dict[str, Any],
    ) -> None:
        """Add a request to the queue, or block if too full."""
        async with self._lock:
            if self._closed:
                raise RuntimeError("BatchProcessor is shut down.")
            if len(self._queue) >= self.max_queue_size:
                # backpressure: wait for next flush
                await self._flush_event.wait()
                self._flush_event.clear()

            self._queue.append((prompt, fut, params))
            logging.debug(f"Enqueued prompt; queue size = {len(self._queue)}")

            # trigger immediate flush if we hit batch size
            if len(self._queue) >= self.max_batch:
                self._flush_event.set()

    async def _flush_loop(self) -> None:
        """Flush periodically or when triggered."""
        try:
            while not self._closed:
                # wait for either the interval or an explicit trigger
                try:
                    await asyncio.wait_for(self._flush_event.wait(), timeout=self.flush_interval)
                except asyncio.TimeoutError:
                    pass

                async with self._lock:
                    if self._queue:
                        await self._flush_once()
                        # wake up any waiting enqueuers
                        self._flush_event.clear()
                        self._flush_event.set()
        except asyncio.CancelledError:
            # on shutdown, flush remaining
            async with self._lock:
                if self._queue:
                    await self._flush_once()

    async def _flush_once(self) -> None:
        """Collect the batch, call LLM, and resolve futures."""
        batch = self._queue
        self._queue = []

        prompts, futures, params_list = zip(*batch)
        # enforce homogeneous hyperparams / could also split into sub‐batches by differing params
        common_params = params_list[0]
        try:
            results = await self.client.generate_batch(list(prompts), common_params)
            for fut, text in zip(futures, results):
                fut.set_result(text)
        except Exception as e:
            logging.exception("Error during batch generation")
            for fut in futures:
                if not fut.done():
                    fut.set_exception(e)

    async def shutdown(self) -> None:
        """Cancel the loop and wait for it to finish flushing."""
        async with self._lock:
            self._closed = True
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task



