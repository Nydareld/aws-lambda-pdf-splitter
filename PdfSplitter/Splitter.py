from ConfigEnv import Config
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
import boto3


class Splitter():
    """docstring for Splitter."""

    def __init__(self, configFile = None):
        self._config = Config(configFile)
        self._cachePage = {}
        self._cachePdf = {}
        self._s3 = boto3.resource(
            's3',
            'eu-west-1',
            aws_access_key_id=self._config.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=self._config.get("AWS_SECRET_ACCESS_KEY"),
            aws_session_token= self._config.get("AWS_SESSION_TOKEN")
        )
        self._bucket = self._s3.Bucket(self._config.get("AWS_S3_BUCKET"))


    def _downloadAndCache(self,fileKey):
        s3Object = self._s3.Object(self._config.get("AWS_S3_BUCKET"),fileKey)
        self._cachePdf[fileKey] = io.BytesIO(s3Object.get()["Body"].read())


    def _cachePdfOneFile(self,fileKey):
        self._downloadAndCache(fileKey)

        pdfBuffer = self._cachePdf[fileKey]
        self._cachePage[fileKey] = []
        cachePage = self._cachePage[fileKey]

        infileReader = PdfFileReader(pdfBuffer)

        for i in range(infileReader.getNumPages()):
            page = infileReader.getPage(i)
            cachePage.append(page)

    def _getOnePage(self,fileKey,page):
        if fileKey not in self._cachePage:
            self._cachePdfOneFile(fileKey)
        return self._cachePage[fileKey][page]
