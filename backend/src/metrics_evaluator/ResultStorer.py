from io import BytesIO

import db_client


class ResultStorer:
    def __init__(self, wui_id, metric_id, results):
        self.wui_id = wui_id
        self.results = results
        self.metric_id = metric_id

    def store_result(self):
        processed_result = []
        for result in self.results:
            if isinstance(result, BytesIO):  # need to store file differently
                # upload file to storage bucket and retrieve its URL
                file_url = db_client.upload_file(
                    file=result,
                    bucket_path='results',
                    file_extension='.png'
                )
                # change the corresponding result to its URL
                processed_result.append(file_url)
            else:
                processed_result.append(result)

        # store result metadata to the database
        db_client.insert_metric_result_metadata(
            wui_id=self.wui_id,
            metric_id=self.metric_id,
            results=processed_result
        )

