---
paths:
  - "**/*.{vue,js,jsx,ts,tsx}"
  - "**/wagmi/**"
  - "**/rainbowkit/**"
---

# wagmi 规范

- 合约交易的执行得使用模拟交易,这样万一有报错就会先提示出来,并且应该使用 shortMessage
