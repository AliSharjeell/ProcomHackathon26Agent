# UI Component Gallery

Generated on: Sat Feb 14 18:26:08 2026

## Simple Data Retrieval (Text Bubble or Info)
**User:** `What is my current balance?`

**Voice:** "Your current balance is PKR 16,820."

### Visual: `TEXT_BUBBLE`
```json
{
  "type": "TEXT_BUBBLE",
  "data": {
    "markdown": "Current Balance: PKR 16,820"
  }
}
```

---
## Missing Information (Composite Form)
**User:** `I want to transfer money.`

**Voice:** "To transfer money, I need to know the recipient's details. Please provide the recipient's name or account number."

### Visual: `COMPOSITE_FORM`
```json
{
  "type": "COMPOSITE_FORM",
  "state": "initial",
  "data": {
    "title": "Transfer Money",
    "widgets": [
      {
        "id": "recipient_id",
        "type": "input",
        "label": "Recipient's Name or Account Number"
      }
    ]
  }
}
```

---
## Transfer Preview (Confirmation Card)
**User:** `Transfer 5000 to Ali.`

**Voice:** "Confirm transfer of PKR 5,000 to Ali Khan. Your balance will be PKR 11,820 after this transfer."

### Visual: `CONFIRMATION_CARD`
```json
{
  "type": "CONFIRMATION_CARD",
  "state": "initial",
  "data": {
    "title": "Confirm Transfer",
    "fields": [
      {
        "label": "To",
        "value": "Ali Khan"
      },
      {
        "label": "Amount",
        "value": "PKR 5,000"
      }
    ]
  }
}
```

---
## List Items (Selection List / Info Table)
**User:** `Show me my cards.`

**Voice:** "Here are your cards: 7b95eaeb-bbb0-4df7-a1ba-9bd364de64b7 (ending in 9002), a65d17ac-88d0-4609-85fe-59e41d1a00b9 (ending in 1223), d18bf081-aea3-4783-b4fc-06923f7fe2b2 (ending in 6255), 60a06f71-1a82-44b2-ad03-f132e377bb10 (ending in 2646), 4684b54a-8120-44f7-bf0e-80b667ce20d0 (ending in 2881), 6c26ca80-39b7-4262-94b0-26a37ac801b5 (ending in 9000), 5474550b-2949-4553-a8e4-85b97d5e2878 (ending in 9001)."

### Visual: `SELECTION_LIST`
```json
{
  "type": "SELECTION_LIST",
  "state": "initial",
  "data": {
    "title": "Your Cards",
    "items": [
      {
        "id": "7b95eaeb-bbb0-4df7-a1ba-9bd364de64b7",
        "title": "**** **** **** 9002"
      },
      {
        "id": "a65d17ac-88d0-4609-85fe-59e41d1a00b9",
        "title": "**** **** **** 1223"
      },
      {
        "id": "d18bf081-aea3-4783-b4fc-06923f7fe2b2",
        "title": "**** **** **** 6255"
      },
      {
        "id": "60a06f71-1a82-44b2-ad03-f132e377bb10",
        "title": "**** **** **** 2646"
      },
      {
        "id": "4684b54a-8120-44f7-bf0e-80b667ce20d0",
        "title": "**** **** **** 2881"
      },
      {
        "id": "6c26ca80-39b7-4262-94b0-26a37ac801b5",
        "title": "**** **** **** 9000"
      },
      {
        "id": "5474550b-2949-4553-a8e4-85b97d5e2878",
        "title": "**** **** **** 9001"
      }
    ]
  }
}
```

---
## Action Confirmation (Confirmation / Security)
**User:** `Freeze my Visa card.`

**Voice:** "I apologize, it seems there was an issue with the PIN. To freeze your Visa card, I need you to enter your 4-digit PIN for verification."

### Visual: `SECURITY_CHALLENGE`
```json
{
  "type": "SECURITY_CHALLENGE",
  "data": {
    "method": "pin",
    "length": 4
  }
}
```

---
## Bill Payment Flow (Composite Form / Confirmation)
**User:** `Pay my K-Electric bill.`

**Voice:** "To pay your K-Electric bill, I need to know your consumer number or biller ID. Please provide one of these details."

### Visual: `COMPOSITE_FORM`
```json
{
  "type": "COMPOSITE_FORM",
  "state": "initial",
  "data": {
    "title": "Pay K-Electric Bill",
    "widgets": [
      {
        "id": "consumer_number",
        "type": "input",
        "label": "Consumer Number"
      },
      {
        "id": "biller_id",
        "type": "input",
        "label": "Biller ID (optional)"
      }
    ]
  }
}
```

---
## Data Visualization (Info Table)
**User:** `How much did I spend last month?`

**Voice:** "No Voice"

> No Visual Data

---
