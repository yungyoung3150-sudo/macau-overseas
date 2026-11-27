# Claude Docs 탭 채우기 (공통 지시)

목표: 국내팀 팀장님이 11/6부터 마카오 CS를 대신 받는다. 인수인계 원문을 Claude Doc(https://claude.ai/artifact/X5wkUURNQ8h14wiBeByjxq) 탭에 옮긴다. 내용은 이미 마크다운 파일로 준비돼 있다. 너는 글을 고치지 않고 그대로 옮긴다.

도구: mcp__claude_ai_Claude_Docs__update (ToolSearch "select:mcp__claude_ai_Claude_Docs__update" 로 이미 있음). 문서 container = {"kind":"project","id":"f3a2e01f-dd8b-4163-ac6c-18e97b87f10e"}.

각 탭마다:
1. 첫 청크 파일(NN-0.md)은 그 탭의 pending 블록을 교체한다:
   update(ref={"object":"node","id":"<body id>"}, engine="prose", container=C,
     payload={"ops":[{"op":"replace","target":{"kind":"blocks","ids":["<pending id>"]},
       "with":{"from":{"kind":"inline","content":"<파일 내용 그대로>"},"as":"markdown"}}]})
2. 다음 청크(NN-1.md, NN-2.md …)는 탭 끝에 덧붙인다:
   payload={"ops":[{"op":"insert","target":{"kind":"root"},"side":"end",
     "source":{"from":{"kind":"inline","content":"<파일 내용>"},"as":"markdown"}}]}
3. 한 호출에 청크 하나. 파일은 Read 로 읽어 내용을 한 글자도 바꾸지 말고 넣는다(한글은 리터럴 UTF-8, 유니코드 이스케이프 금지).
4. 거절(refused)되면 code 와 detail 을 보고 고쳐서 다시 보낸다. 내용이 너무 크다는 거절이면 그 청크를 ### 제목 경계에서 둘로 나눠 두 번 보낸다.
5. 다른 탭·다른 노드는 건드리지 않는다. 로컬 파일 편집 금지.

끝나면 보고: 탭별로 보낸 청크 수, 각 ack 의 verdict, 거절과 처리 내역. 짧게.
