from app.services.masking import mask_text, unmask_text


def test_masks_email_phone_nric_and_restores():
    text = "Mail jane.tan@client.com or call +65 9123 4567. NRIC S1234567D."
    masked, mapping = mask_text(text)
    assert "jane.tan@client.com" not in masked and "9123" not in masked and "S1234567D" not in masked
    assert unmask_text(masked, mapping) == text


def test_plain_text_unchanged():
    masked, mapping = mask_text("Please send the letter by Friday.")
    assert masked == "Please send the letter by Friday." and mapping == {}
