# Project Reflection

This project demonstrates how a language model can help convert unstructured hostel maintenance complaints into consistent work orders. Students and hostel residents often report issues using informal language, incomplete descriptions, spelling mistakes, or emotional wording. A local language model can interpret these descriptions and propose structured fields such as room, issue category, urgency, and a short summary.

A major design decision was to keep important safety and business rules in ordinary Python rather than relying entirely on the model. The model is useful for understanding natural language, but it can make mistakes. Python validates the issue category, checks room formats, applies a safety-word rule, detects duplicates, assigns maintenance teams, and calculates due dates. This separation makes the system easier to test and explain.

The safety design is especially important. Sparks, burning smells, electric shocks, water near electrical fittings, and flooding must be treated as urgent. The program never makes a ticket less urgent. A warden must read every urgent ticket and remains responsible for assigning and closing work. The system is only a sorting assistant and cannot replace human judgment.

The project uses llama.cpp with a quantized local model. This avoids the need for a cloud API key and allows the classifier to run without sending complaint text to an external model provider after the initial model download. The trade-off is that CPU-only inference can be slower, and the computer must have enough memory and storage.

Testing should include normal complaints, missing room numbers, duplicate reports, misleading capital letters, and safety-related phrases. Evaluation results should be reviewed manually because a correct JSON response does not automatically mean the classification is correct. The project can be improved by adding more realistic sample complaints, better duplicate history, stronger room parsing, and a simple warden review interface.

Overall, this project shows that AI is most useful when combined with clear rules, validation, testing, and human oversight. The model handles language understanding, Python enforces predictable rules, and the warden makes the final operational decisions.
