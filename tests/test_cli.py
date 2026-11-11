import json
import pytest
import subprocess
import sys
from pathlib import Path

@pytest.fixture
def sample_sipl_file(tmp_path):
    file_path = tmp_path / "test.sipl"
    file_path.write_text("begin X := 5; Y := X + 2 end", encoding="utf-8")
    return file_path

def run_cli_cmd(args):
    cmd = [sys.executable, "-m", "sipl.cli"] + args
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res

def test_cli_check(sample_sipl_file):
    res = run_cli_cmd(["check", str(sample_sipl_file), "--json"])
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["status"] == "ok"

def test_cli_parse(sample_sipl_file):
    res = run_cli_cmd(["parse", str(sample_sipl_file), "--json"])
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["status"] == "ok"
    assert "ast" in data

def test_cli_run(sample_sipl_file):
    res = run_cli_cmd(["run", str(sample_sipl_file), "--json"])
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["status"] == "ok"
    assert data["final_state"]["Y"] == 7

def test_cli_trace(sample_sipl_file):
    res = run_cli_cmd(["trace", str(sample_sipl_file), "--json"])
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["status"] == "ok"
    assert "trace" in data
    assert len(data["trace"]) > 0