export function getComments() {
  return ([
    {commentID: 0, line: 4, author: "Luke", text: `I recommend the following change:
4c4
<       self.choices = choices
---
>       self.choices = choic`, 
      subcomments: [
        {author: "Simon", text: "These are terrible changes.\nI will not accept this!"},
        {author: "Luke", text: "I disagree, these changes will improve your code"}
      ]
    },
    {commentID: 1, line: 13, author: "Luke", text: `I reccomend the following change:
13c13
<       self.questions = questions
---
>       self.questions = estions`, 
      subcomments: [
        {author: "Simon", text: "These are terrible changes.\nI will not accept this!"},
        {author: "Luke", text: "I disagree, these changes will improve your code"}
      ]
    },
    {commentID: 2, line: 23, author: "Luke", text: `I recommend the following change:
23c23
<           user_answer = input("Yr answer: ")
---
>           user_answer = input("Your answer: ")`,
      subcomments: [
        {author: "Simon", text: "These are terrible changes.\nI will not accept this!"},
        {author: "Luke", text: "I disagree, these changes will improve your code"}
      ]
    }
  ])
}