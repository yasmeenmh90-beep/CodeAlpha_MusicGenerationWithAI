from fastapi.testclient import TestClient
import pretty_midi as pm
import api
import conditioning

client = TestClient(api.app)

def test_health():
    assert client.get("/health").status_code == 200
    assert "conditioned_ready" in client.get("/health").json()

def test_validation():
    for body in [{"bpm": 0}, {"length": 9999}, {"scale": "invalid"}, {"seed": -1}]:
        assert client.post("/generate", json=body).status_code == 422

def test_missing_track():
    assert client.get("/tracks/00000000-0000-0000-0000-000000000000/wav").status_code == 404

def test_scale():
    midi = pm.PrettyMIDI()
    inst = pm.Instrument(0)
    inst.notes.append(pm.Note(80, 61, 0, 1))
    midi.instruments.append(inst)
    _, tokens = conditioning.constrain(midi, [61,128], 0, "major")
    assert tokens == [60,128]
    assert inst.notes[0].pitch == 60

def test_generation(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "ROOT", tmp_path)
    response = client.post("/generate", json={"length":16,"seed":42})
    assert response.status_code == 200
    track = response.json()
    assert len(track["tokens"]) == 16
    assert client.get(track["wav"]).content.startswith(b"RIFF")
    assert client.get(track["midi"]).content.startswith(b"MThd")

def test_history():
    assert isinstance(client.get("/training/history").json()["original"], list)
