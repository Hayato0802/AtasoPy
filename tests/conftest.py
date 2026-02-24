"""テスト設定 - プロジェクトルートをsys.pathに追加"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
