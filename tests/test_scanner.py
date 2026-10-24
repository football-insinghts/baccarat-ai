import unittest
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock

from PIL import Image

from scanner import prepare_image, stream_analysis


class ScannerTests(unittest.TestCase):
    def test_png_compression_preserves_dimensions_and_pixels(self):
        output = BytesIO()
        Image.new("RGB", (800, 600), "navy").save(output, format="PNG", compress_level=0)
        original = output.getvalue()
        image = Image.open(BytesIO(original))
        payload = prepare_image(original, image)
        restored = Image.open(BytesIO(payload["data"]))
        self.assertEqual(image.size, restored.size)
        self.assertEqual(image.tobytes(), restored.tobytes())
        self.assertLess(len(payload["data"]), len(original))

    def test_jpeg_is_sent_without_reencoding(self):
        output = BytesIO()
        Image.new("RGB", (100, 80), "green").save(output, format="JPEG")
        original = output.getvalue()
        payload = prepare_image(original, Image.open(BytesIO(original)))
        self.assertEqual(payload, {"mime_type": "image/jpeg", "data": original})

    def test_stream_preserves_prompt_and_yields_before_completion(self):
        def chunks():
            yield SimpleNamespace(text="first ", candidates=[])
            yield SimpleNamespace(text="second", candidates=[])
        model = Mock()
        model.generate_content.return_value = chunks()
        prompt = "original prompt including 20 predictions"
        payload = {"data": b"image", "mime_type": "image/png"}
        stream = stream_analysis(model, payload, prompt)
        self.assertEqual(next(stream), "first ")
        self.assertEqual(list(stream), ["second"])
        model.generate_content.assert_called_once_with(
            [payload, prompt], stream=True,
            request_options={"timeout": 90, "retry": None},
        )

    def test_truncated_response_is_not_treated_as_success(self):
        model = Mock()
        candidate = SimpleNamespace(finish_reason=SimpleNamespace(name="MAX_TOKENS"))
        model.generate_content.return_value = [SimpleNamespace(text="partial", candidates=[candidate])]
        with self.assertRaises(ValueError):
            list(stream_analysis(model, {}, "original"))

    def test_stream_error_is_propagated(self):
        def chunks():
            yield SimpleNamespace(text="partial", candidates=[])
            raise ConnectionError("connection lost")
        model = Mock()
        model.generate_content.return_value = chunks()
        stream = stream_analysis(model, {}, "original")
        self.assertEqual(next(stream), "partial")
        with self.assertRaises(ConnectionError):
            next(stream)


if __name__ == "__main__":
    unittest.main()
