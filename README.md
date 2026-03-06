# LIX

LIX and RIX readability scores for Scandinavian languages (Norwegian, Swedish, Danish).

Zero dependencies. Typed. Tested.

## Install

```bash
pip install git+https://github.com/eiriks/python-lix.git
```

## Usage

```python
import lix

result = lix.compute("Katten satt på matta. Den var varm.", language="nb")
print(result.lix)         # LIX score
print(result.rix)         # RIX score
print(result.difficulty)  # Difficulty.VERY_EASY
```

## Supported languages

| Code | Language |
|------|----------|
| `nb` | Norwegian Bokmål |
| `nn` | Norwegian Nynorsk |
| `da` | Danish |
| `sv` | Swedish |


## Arv og opphav
Jeg implementerte [LIX](http://sv.wikipedia.org/wiki/LIX ) en gang i tiden [lenke](https://github.com/eiriks/samstemmer/blob/08be6a063c077c9654192d792c2c80e544ce6385/fylkesperspektiv/management/commands/compute_lix.py#L11) i python for Norsk bokmål.

Trengte å gjenbruke den i dag og fant https://github.com/QC20/LIX-RIX-Danish-NLP-Language-Scores som også har med svensk og dansk og nynorsk.

Dette repoet er rasultatet av at en LLM har slått disse to forsøkene sammen. 

