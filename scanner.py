"""Transport helpers: preserve image pixels and the caller's original prompt."""

from io import BytesIO


def prepare_image(original_bytes, image):
    """Choose the smaller lossless representation without resizing the image."""
    if image.format == "JPEG":
        return {"mime_type": "image/jpeg", "data": original_bytes}
    output = BytesIO()
    image.save(output, format="PNG", compress_level=6)
    png_bytes = output.getvalue()
    if image.format != "PNG" or len(png_bytes) < len(original_bytes):
        return {"mime_type": "image/png", "data": png_bytes}
    return {"mime_type": "image/png", "data": original_bytes}


def stream_analysis(model, image_payload, prompt):
    """Yield text early; never accept a truncated stream as a complete report."""
    response = model.generate_content(
        [image_payload, prompt],
        stream=True,
        request_options={"timeout": 90, "retry": None},
    )
    for chunk in response:
        candidates = getattr(chunk, "candidates", None)
        if candidates:
            reason = getattr(candidates[0], "finish_reason", None)
            reason_name = getattr(reason, "name", None)
            if reason_name and reason_name not in ("STOP", "FINISH_REASON_UNSPECIFIED"):
                raise ValueError("Analysis did not complete")
        try:
            text = chunk.text
        except ValueError:
            if candidates and reason_name == "STOP":
                continue
            raise
        if text:
            yield text
