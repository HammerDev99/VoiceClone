"""Tests de los DTOs del dominio: inmutabilidad y propiedades derivadas."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from voiceclone.domain.models import (
    AccountInfo,
    ClonedVoice,
    ConversationTurn,
    GeneratedSpeech,
    SpeechRequest,
    VoiceSample,
)


def test_voice_sample_name_property() -> None:
    sample = VoiceSample(path=Path("audios/clip_01.m4a"))
    assert sample.name == "clip_01.m4a"


def test_account_info_remaining_normal() -> None:
    info = AccountInfo(tier="starter", characters_used=300, characters_limit=1000)
    assert info.characters_remaining == 700


def test_account_info_remaining_never_negative() -> None:
    info = AccountInfo(tier="free", characters_used=1500, characters_limit=1000)
    assert info.characters_remaining == 0


@pytest.mark.parametrize(
    "dto",
    [
        VoiceSample(path=Path("a.m4a")),
        ClonedVoice(voice_id="v1", name="Alexander"),
        SpeechRequest(text="hola", voice_id="v1", model_id="m", output_format="mp3_44100_128"),
        GeneratedSpeech(path=Path("output/a.mp3"), bytes_written=10),
        ConversationTurn(role="user", content="hola"),
        AccountInfo(tier="free", characters_used=0, characters_limit=10),
    ],
)
def test_dtos_son_inmutables(dto: object) -> None:
    field = dataclasses.fields(dto)[0].name  # type: ignore[arg-type]
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(dto, field, "mutado")
