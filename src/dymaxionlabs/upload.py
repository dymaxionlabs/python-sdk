import requests
from google.resumable_media.requests import ResumableUpload


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

    def transmit_next_chunk(self):
        method, url, payload, headers = self._prepare_request()
        response = requests.put(
            url,
            data=payload,
            headers=headers,
        )
        self._process_response(response, len(payload))
        return response
