import json, sys, os, re, traceback, pathlib
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
import bellman, meaning_map_training.compare as C
from bellman.factory.elaboration import elaborate_text
print("bellman from:", bellman.__file__); print("compare from:", C.__file__)
DOC = """@stage: buffer_stock

β : (0,1)
ρ : (1, inf)
R : ℝ₊₊
μ_y : ℝ
σ_y : ℝ₊
y : ℝ₊₊
y ~ LogNormal(μ_y, σ_y)

𝑢(c : ℝ₊₊) := c^(1-ρ)/(1-ρ)

[id=arvl_to_dcsn, (b : ℝ₊, y) : !arvl -> (w : ℝ₊₊) : !dcsn] {
    w = R*b + y                  :: [id=resources]
}
[id=dcsn_to_cntn, (w, c : ℝ₊₊ @ !ctrl) : !dcsn -> (a : ℝ₊) : !cntn] {
    a = w - c                    :: [id=savings]
}
[id=cntn_to_dcsn, (V[>] : ℝ @ !vlu, c) : !cntn -> (V : ℝ @ !vlu) : !dcsn] {
    V = 𝑢(c) + β*V[>]            :: [id=value]
}
[id=dcsn_to_arvl, (V) : !dcsn -> (V[<] : ℝ @ !vlu) : !arvl] {
    V[<] = E_{y}(V)              :: [id=value]
}
[id=policy, (V[>]) : !cntn -> (c) : !dcsn] {
    c = argmax_{c}(𝑢(c) + β*V[>]) :: [id=choice]
}
"""
DECK = DOC.replace("(b : ℝ₊, y)", "(k : ℝ₊, y)").replace("(w : ℝ₊₊)", "(m : ℝ₊₊)").replace("w = R*b + y", "m = R*k + y").replace("(w, c :", "(m, c :").replace("a = w - c", "a = m - c")
assert " b " not in DECK and "w =" not in DECK
def sub(a,b):
    assert a in DECK, a
    return DECK.replace(a,b)
CASES = {
 "deck file (should construct)": DECK,
 "doc example (should construct)": DOC,
 "shock outside expectation, y NOT in inputs: V[<]=E_{y}(V)+y": sub("V[<] = E_{y}(V)              ::", "V[<] = E_{y}(V) + y          ::"),
 "shock outside expectation, y IN inputs: V[<]=E_{y}(V)+y": sub("V[<] = E_{y}(V)              ::", "V[<] = E_{y}(V) + y          ::").replace("[id=dcsn_to_arvl, (V) : !dcsn", "[id=dcsn_to_arvl, (V, y) : !dcsn"),
 "continuation value at decision perch: cntn_to_dcsn input side !dcsn": sub("(V[>] : ℝ @ !vlu, c) : !cntn", "(V[>] : ℝ @ !vlu, c) : !dcsn"),
 "continuation value declared @ !dcsn on the field": sub("(V[>] : ℝ @ !vlu, c) : !cntn", "(V[>] : ℝ @ !dcsn, c) : !cntn"),
 "mean of shock in transition: m=R*k+exp(mu+sig^2/2)": sub("m = R*k + y", "m = R*k + exp(μ_y + σ_y^2/2)"),
 "second beta in expectation block": sub("V[<] = E_{y}(V)              ::", "V[<] = β*E_{y}(V)            ::"),
}
for name, text in CASES.items():
    try:
        s = elaborate_text(text, "deck.bl")
        print(f"[ACCEPT] {name}  -> {type(s).__name__}")
    except Exception as e:
        rule = getattr(e,'rule',None) or (re.search(r'rule ([a-z-]+)', str(e)) or [None,None])[1]
        print(f"[REFUSE] {name}\n    {type(e).__name__} rule={rule}\n    {str(e)[:420]!r}")
(out/"deck.bl").write_text(DECK, encoding="utf8"); (out/"doc.bl").write_text(DOC, encoding="utf8")
try:
    l, r = C._items_of_file(str(out/"deck.bl")), C._items_of_file(str(out/"doc.bl"))
    p = C.compare(l, r)
    print("COMPARE verdict:", p["verdict"], "share:", p["share_matched"], "renaming:", json.dumps(p["renaming"], ensure_ascii=False), "source:", p["renaming_source"], "first_diff:", json.dumps(p["first_difference"], ensure_ascii=False)[:300], "undecided:", len(p["undecided_kernels"]))
except Exception:
    traceback.print_exc()
