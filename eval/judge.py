from openai import OpenAI
 
client = OpenAI()
 
JUDGE_MODEL = "gpt-4.1"
 
 

RUBRICS = {

    "exact_figure": """Grade CORRECT only if the numeric value matches the ground truth.
- Formatting differences are ACCEPTABLE ($13.5B = $13,500 million = 13,549).
- Reasonable rounding is ACCEPTABLE ($416.16B vs $416.2B vs "about $416 billion").
- Extra context or explanation around the number is ACCEPTABLE.
- A DIFFERENT number is INCORRECT.
- Refusing to answer ("I couldn't find that in the filing") is INCORRECT, because
  this question IS answerable from the filing.""",
 
    "synthesis": """Grade CORRECT if the answer captures the same substantive THEMES as the
ground truth.
- The answer need NOT mention every detail listed in the ground truth.
- Different phrasing, emphasis, structure, or level of detail is ACCEPTABLE.
- Additional accurate detail beyond the ground truth is ACCEPTABLE.
- Grade INCORRECT only if the answer CONTRADICTS the ground truth, misses the
  central point entirely, or refuses to answer.""",
 

    "cross_company": """Grade CORRECT if the answer reaches the same overall CONCLUSION or
COMPARISON as the ground truth.
- Citing different supporting details or figures is ACCEPTABLE.
- Covering only a SUBSET of the companies is ACCEPTABLE, as long as the
  conclusion or comparison still holds.
- Grade INCORRECT if the conclusion is reversed or contradicted, or if the
  answer refuses to engage with the comparison.""",
 
    "unanswerable": """This question CANNOT be answered from the filing. Correct behavior is
to decline.
- Grade CORRECT if the answer declines: says the information is not in the filing,
  not disclosed, cannot be determined, or otherwise refuses to speculate.
- Grade INCORRECT if the answer INVENTS any specific information (a number, an
  address, a projection, a name). That is a hallucination and is the single most
  important failure mode this benchmark exists to catch.""",
}
 
 
JUDGE_PROMPT = """You are grading an AI system's answer against a known-correct answer.
 
QUESTION: {question}
 
GROUND TRUTH: {ground_truth}
 
SYSTEM ANSWER: {answer}
 
GRADING RUBRIC (question category: {category}):
{rubric}
 
Respond with exactly one word: CORRECT or INCORRECT."""
 
 
def judge(question: str, ground_truth: str, answer: str, category: str) -> bool:
    """Grade one answer against ground truth using the rubric for its category.
 
    Returns True if CORRECT, False if INCORRECT.
 
    An unknown category falls back to the `synthesis` rubric — the most permissive
    general-purpose one — so a new category added to the dataset degrades to a
    reasonable default instead of crashing the whole eval run.
    """
    rubric = RUBRICS.get(category, RUBRICS["synthesis"])
 
    resp = client.chat.completions.create(
        model=JUDGE_MODEL,
        temperature=0,  
        messages=[{
            "role": "user",
            "content": JUDGE_PROMPT.format(
                question=question,
                ground_truth=ground_truth,
                answer=answer,
                category=category,
                rubric=rubric,
            ),
        }],
    )
 
    verdict = resp.choices[0].message.content.strip().upper()
 

    return verdict.startswith("CORRECT")
 
 
def judge_with_reason(question: str, ground_truth: str, answer: str,
                      category: str) -> tuple[bool, str]:

    rubric = RUBRICS.get(category, RUBRICS["synthesis"])
 
    prompt = JUDGE_PROMPT.format(
        question=question, ground_truth=ground_truth, answer=answer,
        category=category, rubric=rubric,
    ).replace(
        "Respond with exactly one word: CORRECT or INCORRECT.",
        "Respond with your verdict (CORRECT or INCORRECT) on the first line, "
        "then one sentence explaining why on the second line.",
    )
 
    resp = client.chat.completions.create(
        model=JUDGE_MODEL,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
 
    text = resp.choices[0].message.content.strip()
    lines = text.split("\n", 1)
    verdict = lines[0].strip().upper().startswith("CORRECT")
    reason = lines[1].strip() if len(lines) > 1 else ""
    return verdict, reason
 