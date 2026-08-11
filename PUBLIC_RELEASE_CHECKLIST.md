# Public release checklist

The repository remains private during the competition. Before making it public:

- confirm competition rules permit publication of aggregate metrics and code;
- confirm every public fixture's redistribution terms;
- verify no competition matrix, entity join map, sample-level prediction, vector,
  prompt/response, model weight, credential, local path, or cache is tracked;
- run `uv sync --extra dev` and
  `uv run --locked python -m unittest discover -s tests -v` in `research_code/`;
- run credential, large-file, archive, and absolute-path scans;
- regenerate `SHA256SUMS` from the final tracked payload;
- if a private file ever entered Git history, publish from a newly audited clean
  snapshot or rewrite the history before changing repository visibility.
