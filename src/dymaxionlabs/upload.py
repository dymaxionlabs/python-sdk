import requests
from google.resumable_media.requests import ResumableUpload
from google.resumable_media import common
from six.moves import http_client

_DEFAULT_RETRY_STRATEGY = common.RetryStrategy()
RETRYABLE = (
    common.TOO_MANY_REQUESTS,
    http_client.INTERNAL_SERVER_ERROR,
    http_client.BAD_GATEWAY,
    http_client.SERVICE_UNAVAILABLE,
    http_client.GATEWAY_TIMEOUT,
)


class CustomResumableUpload(ResumableUpload):
    def initiate(
        self,
        stream,
        metadata,
        content_type,
        resumable_url,
        total_bytes=None,
        stream_final=True,
    ):
        method, url, payload, headers = self._prepare_initiate_request(
            stream,
            metadata,
            content_type,
            total_bytes=total_bytes,
            stream_final=stream_final,
        )
        self._resumable_url = resumable_url
        return True

    @classmethod
    def _transmit_chunk_wait_and_retry(
        cls,
        url,
        payload,
        headers,
        retry_strategy=_DEFAULT_RETRY_STRATEGY,
    ):
        response = requests.put(
            url,
            data=payload,
            headers=headers,
        )
        if response.status_code not in RETRYABLE:
            return response

        total_sleep = 0.0
        num_retries = 0
        base_wait = 0.5  # When doubled will give 1.0
        while retry_strategy.retry_allowed(total_sleep, num_retries):
            base_wait, wait_time = calculate_retry_wait(
                base_wait, retry_strategy.max_sleep)
            num_retries += 1
            total_sleep += wait_time
            time.sleep(wait_time)
            response = requests.put(
                url,
                data=payload,
                headers=headers,
            )
            if response.status_code not in RETRYABLE:
                return response
        return response

    def transmit_next_chunk(self):
        method, url, payload, headers = self._prepare_request()
        response = self._transmit_chunk_wait_and_retry(url, payload, headers)
        self._process_response(response, len(payload))
        return response
