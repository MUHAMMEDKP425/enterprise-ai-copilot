from rag_service import ask_rag


question = "How many days before planned leave should employees submit their request?"

answer = ask_rag(question)

print("\n--- AI ANSWER ---")
print(answer)