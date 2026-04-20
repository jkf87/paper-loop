# Research Paper Production Harness with Claude Code

Claude Code 기반 1인 연구자용 **논문 제작 하네스** 공개 저장소.
학습·평가 코드, 11개 run 실험 로그, 3라운드 피어 리뷰 이력, 4역할 리뷰어 프롬프트 템플릿(영·한)을 전량 공개한다.

> **하네스 개념**
> 1인 연구자의 병목은 노동량이 아니라 **역할 전환 비용과 비판적 자기 검토의 부재**이다.
> 본 하네스는 Claude Code를 오케스트레이터로 삼아 실험 설계 → 학습/평가 → 분석 → 집필 → 피어 리뷰(R1·R2·R3 + 교신교수)의 5단계 파이프라인을 구성하며, **리뷰 지적이 실행 가능한 태스크로 번역되어 첫 단계로 재유입되는 자기참조적 수정 사이클**이 전원 Accept에 이를 때까지 반복된다.

**사례 연구**: 단일 Apple M4 노트북에서 zeroth_korean Whisper Small LoRA 랭크 스케일링 **11회의 실제 학습/평가를 인간 개입 없이 자율 실행**(10회가 리뷰 지적에 의해 유발). 피어 리뷰는 **Reject → Weak Accept → Accept**의 3라운드 궤적을 완주. CER 13.18% → **8.01%(r=64 4시드 평균, 약 39% 상대 감소)**, **시드 분산이 랭크에 반비례**(r=16 SD 0.48 vs r=64 SD 0.07 %p, **6.9×**)하는 부수 관찰까지 산출.

---

## 저장소 구조

```
.
├── README.md                        ← 현재 파일
├── LICENSE                          ← MIT
├── code/                            ← 학습·평가 코드 (9개 파일)
│   ├── train.py                     Standard LoRA 학습/평가 드라이버
│   ├── train_jamo.py                Jamo-LoRA 실험 드라이버 (보류)
│   ├── evaluate_model.py            CER/WER 평가
│   ├── config.py                    하이퍼파라미터
│   ├── data.py                      zeroth_korean 로더
│   ├── run_additional.py            r=8, r=16(다중시드), r=32 실행
│   ├── run_r64_multiseed.py         r=64 다중시드 실행
│   ├── make_figures.py              결과 시각화
│   └── make_figures_final.py        최종 성과/부산물 figure 생성
│
├── experiments/                     ← 11 runs + baseline의 로그 (가중치는 소실)
│   ├── baseline_whisper_small/
│   ├── standard_lora_r4/            (seed 42)
│   ├── standard_lora_r8/            (seed 42)
│   ├── standard_lora_r16/           (seed 42)
│   ├── standard_lora_r16_seed{123,456,789}/
│   ├── standard_lora_r32/           (seed 42)
│   ├── standard_lora_r64/           (seed 42)
│   └── standard_lora_r64_seed{123,456,789}/
│
├── reviews/                         ← 피어 리뷰 이력 (3라운드 × 3명 + 교신교수)
│   ├── round1/                      1차: 시뮬레이션 데이터 적발 → Reject
│   ├── round2/                      2차: 실제 실험 반영 → Weak Accept
│   ├── round3/                      3차: 다중시드 추가 → Accept
│   └── abstract/                    AAICon 1페이지 초록 심사 이력
│
└── prompts/
    └── reviewer_prompt_templates.md ← 4역할(R1·R2·R3·교신교수) 시스템 프롬프트 (영·한)
```

---

## 핵심 결과 재현

### 환경

- macOS 단일 노트북 (Apple Silicon, M1 이상 권장; 본 실험은 M4)
- Python 3.11+, PyTorch 2.x with MPS 백엔드
- HuggingFace Transformers, PEFT, Datasets

### 설치

```bash
pip install torch==2.4.* transformers peft datasets evaluate accelerate jiwer librosa soundfile
```

### 단일 랭크 실행

```bash
cd code
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0   # MPS OOM 회피
python3 train.py 16      # 예: LoRA r=16, seed 42
```

### 다중시드 실행

```bash
python3 run_additional.py       # r=8, r=32 + r=16에 시드 123/456/789
python3 run_r64_multiseed.py    # r=64에 시드 123/456/789
```

### 결과 시각화

```bash
python3 make_figures_final.py
```

---

## 리뷰어 프롬프트 템플릿 사용법

`prompts/reviewer_prompt_templates.md`에 4역할 시스템 프롬프트(영·한)가 수록되어 있다. Claude Code의 `Task` 도구로 다음과 같이 호출한다.

```bash
# 예: Round 2 리뷰 실행
claude-code subagent run \
  --name reviewer-1-methodology \
  --prompt-file ./prompts/reviewer_prompt_templates.md \
  --prompt-section "Reviewer 1 — 방법론 전문가" \
  --input ./paper.tex \
  --input-dir ./experiments/ \
  --output ./reviews/round2/review_1.md

# reviewer 2, 3, advisor 동일 방식으로 병렬 호출
```

**4역할 요약**

| 역할 | 주 질문 | 핵심 규약 |
|---|---|---|
| R1 방법론 | 방법론이 타당한가? | 모든 metrics.json 전수 대조, 수치 불일치 시 Reject |
| R2 실험 | 숫자가 원자료와의 대조를 견디는가? | 실제값/보고값/차분표 작성, 실험 요구 시 시드·경로 명시 |
| R3 가독성 | 주장과 근거가 정렬되어 있는가? | 브랜드 용어 탐지, 중복 섹션·누락 참조 확인 |
| 교신교수 | 제출해도 되는가? | 3 리뷰 통합, 형식 검증, 통계 1개 재계산 증거 |

공통 출력 구조: `Score`(Reject~Accept 5단계) / `Confidence`(1–5) / Summary / Per-section / Major Issues / Recommendations / Decision.

---

## 공개 범위 및 재현성

### 공개
- **학습·평가 코드 전량** (`code/`, 9개 파일)
- **11개 run의 실험 로그** (`experiments/*/metrics.json`, `examples.json`, `adapter_config.json`)
- **3라운드 × 3명 리뷰 + 교신교수 리뷰** (`reviews/`, 15개 md)
- **4역할 리뷰어 프롬프트 템플릿(영·한)** (`prompts/`)

### 미공개 (소실)
- LoRA 어댑터 가중치 `.safetensors` — `run_*.py`가 디스크 관리를 위해 학습 직후 `shutil.rmtree(ckpt_dir)`로 자동 삭제.
- 동일 코드로 단일 M4 노트북에서 1–2시간 재학습 후 HuggingFace Hub 업로드 가능 (4개 어댑터 ~40 MB).

**요컨대**: 가중치만 제외하고 전부 공개, 가중치는 재생성 가능.

---

## 주요 지표

| 구분 | 지표 | 값 |
|---|---|---|
| 하네스 운용 | 실행된 실제 실험 | 11회 (5개 랭크 × seed 42 + r=16·r=64 × 3 extra) |
| 하네스 운용 | 피어 리뷰 라운드 | 3 (Reject → Weak Accept → Accept) |
| 하네스 운용 | 리뷰 촉발 실험 비율 | 10/11 = **90.9%** (인간 개입 0) |
| 하네스 운용 | 총 wall-clock | ~14h (단일 M4 노트북) |
| 사례 연구 | CER (zero-shot → tuned) | 13.18% → **8.01%** (↓39.2% 상대) |
| 사례 연구 | 시드 분산 비율 | **6.9×** (r=16 SD 0.48 vs r=64 SD 0.07 %p) |

---

## 인용

```bibtex
@misc{researchharness2026,
  title        = {A Research Paper Production Harness with Claude Code for Solo Researchers:
                  A Case Study on Korean Whisper LoRA Adaptation},
  author       = {Anonymous},
  year         = {2026},
  howpublished = {AAICon 2026 (Korean AI Friends Conference)},
  note         = {\url{https://github.com/jkf87/research-harness-claude-code}}
}
```

## 라이선스

MIT License. 상세 내용은 `LICENSE` 참조.

## 기여 및 문의

이슈·PR 환영. 특히 다른 도메인(NLP 분류, 멀티모달, RL)에서의 하네스 이식 시도를 공유해주시면 후속 연구에 반영하겠습니다.
