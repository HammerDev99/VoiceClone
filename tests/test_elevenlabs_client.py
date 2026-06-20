"""Tests del cliente de infraestructura de ElevenLabs (con SDK mockeado)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from returns.result import Failure, Success

from voiceclone.domain.models import SpeechRequest
from voiceclone.infrastructure import elevenlabs_client as el


def test_build_client_rechaza_key_vacia() -> None:
    assert isinstance(el.build_client("   "), Failure)


def test_build_client_ok() -> None:
    # ElevenLabs() no hace peticiones de red en la inicializacion.
    assert isinstance(el.build_client("sk_fake"), Success)


def test_get_account_info_exito() -> None:
    client = MagicMock()
    client.user.subscription.get.return_value = MagicMock(
        tier="starter",
        character_count=100,
        character_limit=1000,
        can_use_instant_voice_cloning=True,
    )
    result = el.get_account_info(client)
    assert isinstance(result, Success)
    account = result.unwrap()
    assert account.tier == "starter"
    assert account.characters_remaining == 900
    assert account.can_clone_ivc is True


def test_get_account_info_falla() -> None:
    client = MagicMock()
    client.user.subscription.get.side_effect = RuntimeError("boom")
    assert isinstance(el.get_account_info(client), Failure)


def test_list_voices_exito() -> None:
    # 'name' es un kwarg reservado de MagicMock; se asigna como atributo aparte.
    voice = MagicMock(voice_id="v1")
    voice.name = "Alexander"
    client = MagicMock()
    client.voices.get_all.return_value = MagicMock(voices=[voice])
    result = el.list_voices(client)
    assert isinstance(result, Success)
    voices = result.unwrap()
    assert voices[0].name == "Alexander"
    assert voices[0].voice_id == "v1"


def test_list_voices_falla() -> None:
    client = MagicMock()
    client.voices.get_all.side_effect = RuntimeError("boom")
    assert isinstance(el.list_voices(client), Failure)


def test_create_instant_voice_sin_muestras() -> None:
    assert isinstance(el.create_instant_voice(MagicMock(), "Alexander", [], "desc"), Failure)


def test_create_instant_voice_exito(tmp_path: Path) -> None:
    sample = tmp_path / "clip.m4a"
    sample.write_bytes(b"audio")
    client = MagicMock()
    client.voices.ivc.create.return_value = MagicMock(voice_id="voice_xyz")
    result = el.create_instant_voice(client, "Alexander", [sample], "desc")
    assert isinstance(result, Success)
    assert result.unwrap().voice_id == "voice_xyz"


def test_create_instant_voice_falla(tmp_path: Path) -> None:
    sample = tmp_path / "clip.m4a"
    sample.write_bytes(b"audio")
    client = MagicMock()
    client.voices.ivc.create.side_effect = RuntimeError("boom")
    assert isinstance(el.create_instant_voice(client, "Alexander", [sample], "desc"), Failure)


def _request() -> SpeechRequest:
    return SpeechRequest(
        text="hola", voice_id="v1", model_id="eleven_multilingual_v2", output_format="mp3_44100_128"
    )


def test_text_to_speech_exito() -> None:
    client = MagicMock()
    client.text_to_speech.convert.return_value = iter([b"aa", b"bb"])
    result = el.text_to_speech(client, _request())
    assert isinstance(result, Success)
    assert result.unwrap() == b"aabb"


def test_text_to_speech_vacio_es_fallo() -> None:
    client = MagicMock()
    client.text_to_speech.convert.return_value = iter([])
    assert isinstance(el.text_to_speech(client, _request()), Failure)


def test_text_to_speech_falla() -> None:
    client = MagicMock()
    client.text_to_speech.convert.side_effect = RuntimeError("boom")
    assert isinstance(el.text_to_speech(client, _request()), Failure)
