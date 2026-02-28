from llm.gigachat import ask_gigachat

prompt = "Подбери женский сладкий зимний аромат с ванилью"

try:
    answer = ask_gigachat(prompt)
    print("Ответ от GigaChat:\n")
    print(answer)
except Exception as e:
    print("Ошибка:", e)
