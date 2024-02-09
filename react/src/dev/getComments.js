export function getComments() {
  return ([
    {commentID: 0, author: "Luke", text: `4c4
<       self.choices = choices
---
>       self.choices = choic
13c13
<       self.questions = questions
---
>       self.questions = estions
23c23
<           user_answer = input("Your answer: ")
---
>           user_answer = input("Yr answer: ")`, 
        subcomments: [
        {author: "Simon", text: "These are terrible changes.\nDo not approve these."},
        {author: "Frank", text: "I love these changes"}
        ]
    },
    {commentID: 1, author: "Simon", text: "Change 2", subcomments: null},
    {commentID: 2, author: "Frank", text: "Change 3", subcomments: null},
    {commentID: 3, author: "Hai", text: "Change 4", subcomments: null}
    ]
  )
}