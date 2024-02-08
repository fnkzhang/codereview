export function getCode() {
  return `class Question:
  def __init__(self, text, choices, correct_choice):
      self.text = text
      self.choices = choices
      self.correct_choice = correct_choice

  def is_correct(self, user_answer):
      return user_answer == self.correct_choice


class Quiz:
  def __init__(self, questions):
      self.questions = questions
      self.score = 0

  def run(self):
      print("Welcome to the Quiz!")
      for i, question in enumerate(self.questions, start=1):
          print(f"\\nQuestion {i}: {question.text}")
          for j, choice in enumerate(question.choices, start=1):
              print(f"{j}. {choice}")

          user_answer = input("Your answer: ")
          if user_answer.isdigit() and 1 <= int(user_answer) <= len(question.choices):
              user_answer = int(user_answer)
              if question.is_correct(user_answer):
                  print("Correct!\\n")
                  self.score += 1
              else:
                  print(f"Wrong! The correct answer was {question.correct_choice}\\n")
          else:
              print("Invalid choice. Skipping to the next question.\\n")

      print(f"Quiz completed! Your score: {self.score}/{len(self.questions)}")


# Sample Quiz
questions = [
  Question("What is the capital of France?", ["Berlin", "Paris", "Madrid", "Rome"], 2),
  Question("Which planet is known as the Red Planet?", ["Mars", "Venus", "Jupiter", "Saturn"], 1),
  Question("What is the largest mammal?", ["Elephant", "Blue Whale", "Giraffe", "Hippopotamus"], 2),
]

quiz = Quiz(questions)
quiz.run()
`;
}