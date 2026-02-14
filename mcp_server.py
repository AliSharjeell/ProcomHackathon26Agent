"""
Procom Banking MCP Server
─────────────────────────
Exposes every banking API endpoint as an MCP tool so that any
AI agent (Claude Desktop, Cursor, etc.) can interact with the bank.

Usage:
    python mcp_server/server.py                        # stdio transport (default)
    fastmcp run mcp_server/server.py:mcp               # via CLI
    fastmcp dev mcp_server/server.py:mcp               # MCP Inspector UI
"""

import json
import uuid
import os
from typing import Optional
from decimal import Decimal

import httpx
from fastmcp import FastMCP

# ── Configuration ─────────────────────────────────────────────
# Use env var for base URL to avoid hardcoding devtunnel
BASE_URL = os.getenv("BANKING_API_URL", "http://localhost:8000/api/v1")
TIMEOUT = 30.0  # seconds
# Get token/key from environment for authentication
API_KEY = os.getenv("PROCOM_API_KEY", "demo-token")

# ── Server ────────────────────────────────────────────────────
mcp = FastMCP(
    "Procom Banking",
    instructions=(
        "You are a helpful banking assistant for Procom Bank. "
        "Use these tools to check balances, transfer money, pay bills, "
        "manage cards, and view spending analytics on behalf of the user. "
        "Always preview transfers before executing them. "
        "Never fabricate financial data — always call the tool."
    ),
)


# ── Helpers ───────────────────────────────────────────────────

def _idempotency_key() -> str:
    """Generate a unique idempotency key for mutation requests."""
    return f"mcp-{uuid.uuid4().hex[:12]}"


async def _get(path: str, params: dict | None = None) -> str:
    """HTTP GET wrapper that returns a formatted JSON string."""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    import sys
    print(f"DEBUG_MCP: GET {BASE_URL}{path} Headers={headers}", file=sys.stderr)
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            resp = await client.get(f"{BASE_URL}{path}", params=params, headers=headers)
            print(f"DEBUG_MCP: RESP {resp.status_code} {resp.text[:100]}", file=sys.stderr)
            return _format_response(resp)
        except httpx.RequestError as e:
            print(f"DEBUG_MCP: ERROR {e}", file=sys.stderr)
            return f"❌ Connection Error: {str(e)}"


async def _post(path: str, body: dict, idempotent: bool = True) -> str:
    """HTTP POST wrapper with optional idempotency key."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    if idempotent:
        headers["X-Idempotency-Key"] = _idempotency_key()
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            resp = await client.post(f"{BASE_URL}{path}", json=body, headers=headers)
            return _format_response(resp)
        except httpx.RequestError as e:
            return f"❌ Connection Error: {str(e)}"


async def _put(path: str, body: dict) -> str:
    """HTTP PUT wrapper."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            resp = await client.put(
                f"{BASE_URL}{path}",
                json=body,
                headers=headers,
            )
            return _format_response(resp)
        except httpx.RequestError as e:
            return f"❌ Connection Error: {str(e)}"


def _format_response(resp: httpx.Response) -> str:
    """Convert httpx response to a clean string for the LLM."""
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}

    if resp.status_code >= 400:
        # Surface talkative errors clearly
        if isinstance(data, dict) and "error" in data:
            parts = [f"❌ Error: {data['error']}"]
            if "message" in data:
                parts.append(f"Message: {data['message']}")
            if data.get("suggested_action"):
                parts.append(f"Suggested action: {data['suggested_action']}")
            return "\n".join(parts)
        return f"❌ HTTP {resp.status_code}: {json.dumps(data, indent=2)}"

    return json.dumps(data, indent=2, default=str)


# ══════════════════════════════════════════════════════════════
#  TOOLS
# ══════════════════════════════════════════════════════════════


# ── Accounts ──────────────────────────────────────────────────

@mcp.tool()
async def get_balance() -> str:
    """
    Check the user's current account balance.
    Returns available balance, currency, and account status.
    Call this first before any transfer or payment.
    """
    return await _get("/accounts/balance")


@mcp.tool()
async def account_action(action: str) -> str:
    """
    Freeze or unfreeze the user's bank account.
    Use 'freeze' to lock the account or 'unfreeze' to reactivate it.

    Args:
        action: 'freeze' or 'unfreeze'.
    """
    body: dict = {"action": action}
    return await _post("/accounts/action", body, idempotent=False)


# ── Contacts ──────────────────────────────────────────────────

@mcp.tool()
async def get_contacts() -> str:
    """
    List all saved contacts (beneficiaries).
    Use this to look up a recipient's name or account number
    before making a transfer.
    """
    return await _get("/contacts")


@mcp.tool()
async def create_contact(
    account_number: str,
    nickname: Optional[str] = None,
) -> str:
    """
    Save a new contact by their bank account number.
    The system verifies the account exists and auto-fills the name.
   
    Args:
        account_number: The recipient's bank account number (must be valid).
        nickname: Optional short name for quick reference.
    """
    body: dict = {"account_number": account_number}
    if nickname:
        body["nickname"] = nickname
    return await _post("/contacts", body, idempotent=False)


# ── Transfers ─────────────────────────────────────────────────

@mcp.tool()
async def preview_transfer(
    recipient_id: str,
    amount: float,
    note: Optional[str] = None,
) -> str:
    """
    Preview a transfer WITHOUT moving money (dry run).
    Shows the recipient details, fees, and balance after transfer.
    ALWAYS call this before execute_transfer so the user can confirm.

    Args:
        recipient_id: Contact name, nickname, or account number.
        amount: Amount in PKR to transfer.
        note: Optional description for the transfer.
    """
    body: dict = {"recipient_id": recipient_id, "amount": amount}
    if note:
        body["note"] = note
    return await _post("/transfers/preview", body, idempotent=False)


@mcp.tool()
async def execute_transfer(
    recipient_id: str,
    amount: float,
    pin: str,
    note: Optional[str] = None,
) -> str:
    """
    Actually move money to a recipient. This deducts from the user's balance.
    IMPORTANT: Always call preview_transfer first and get user confirmation.
   
    Args:
        recipient_id: Contact name, nickname, or account number.
        amount: Amount in PKR to transfer.
        pin: The user's 4-digit PIN for verification.
        note: Optional description / memo for the transfer.
    """
    body: dict = {"recipient_id": recipient_id, "amount": amount, "pin": pin}
    if note:
        body["note"] = note
    return await _post("/transfers", body, idempotent=True)


# ── Transactions ──────────────────────────────────────────────

@mcp.tool()
async def get_transactions(
    limit: int = 10,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    """
    View transaction history with optional filters.

    Args:
        limit: Max number of transactions to return (1-100, default 10).
        category: Filter by type: TRANSFER, BILL_PAY, CARD, etc.
        start_date: Start date in ISO format (e.g. '2026-01-01').
        end_date: End date in ISO format (e.g. '2026-01-31').
    """
    params: dict = {"limit": limit}
    if category:
        params["category"] = category
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    return await _get("/transactions", params)


# ── Billers & Payments ────────────────────────────────────────

@mcp.tool()
async def get_billers() -> str:
    """
    List all saved utility billers (electricity, gas, internet, etc.).
    Use this to find a biller_id for quick bill payments.
    """
    return await _get("/billers")


@mcp.tool()
async def save_biller(
    provider_slug: str,
    consumer_number: str,
    nickname: Optional[str] = None,
) -> str:
    """
    Save a new utility biller for quick future payments.

    Args:
        provider_slug: Provider identifier (e.g. 'k_electric', 'sui_gas').
        consumer_number: The meter / consumer number from the bill.
        nickname: Friendly name like 'Home Electricity'.
    """
    body: dict = {
        "provider_slug": provider_slug,
        "consumer_number": consumer_number,
    }
    if nickname:
        body["nickname"] = nickname
    return await _post("/billers", body, idempotent=False)


@mcp.tool()
async def pay_bill(
    consumer_number: Optional[str] = None,
    biller_id: Optional[str] = None,
    biller_name: Optional[str] = None,
    amount: Optional[float] = None,
) -> str:
    """
    Pay a utility bill. Provide EITHER consumer_number OR biller_id.
    If amount is omitted, the system auto-fetches it from the pending invoice.

    Args:
        consumer_number: The meter / consumer number (for ad-hoc payment).
        biller_id: UUID of a saved biller (alternative to consumer_number).
        biller_name: Provider name for the receipt (e.g. 'K-Electric').
        amount: Payment amount in PKR. Omit to auto-pay the invoice amount.
    """
    body: dict = {}
    if consumer_number:
        body["consumer_number"] = consumer_number
    if biller_id:
        body["biller_id"] = biller_id
    if biller_name:
        body["biller_name"] = biller_name
    if amount is not None:
        body["amount"] = amount
    return await _post("/payments/bill", body, idempotent=True)


# ── Cards ─────────────────────────────────────────────────────

@mcp.tool()
async def get_cards() -> str:
    """
    List all cards (physical and virtual) for the user.
    Returns card IDs, masked PANs, status, and limits.
    Use this to find a card_id before freezing, unfreezing, or updating limits.
    """
    return await _get("/cards")


@mcp.tool()
async def get_virtual_cards() -> str:
    """
    List only virtual cards for the user.
    Returns card IDs, masked PANs, status, and limits.
    """
    return await _get("/cards/virtual")


@mcp.tool()
async def create_virtual_card(
    label: str,
    limit: float,
    pin: str,
) -> str:
    """
    Generate a disposable virtual card for safe online shopping.
    Returns a card number (PAN), expiry, CVV, and the card_id.

    Args:
        label: A friendly name like 'Netflix' or 'Online Shopping'.
        limit: Maximum spending limit in PKR.
        pin: The user's 4-digit PIN for verification.
    """
    body: dict = {"label": label, "limit": limit, "pin": pin}
    return await _post("/cards/virtual", body, idempotent=False)


@mcp.tool()
async def card_action(
    card_id: str,
    action: str,
    pin: str,
    reason: Optional[str] = None,
) -> str:
    """
    Freeze or unfreeze a card instantly.

    Args:
        card_id: The UUID of the card.
        action: 'freeze' or 'unfreeze'.
        pin: The user's 4-digit PIN for verification.
        reason: Optional reason for the action.
    """
    body: dict = {"action": action, "pin": pin}
    if reason:
        body["reason"] = reason
    return await _post(f"/cards/{card_id}/action", body, idempotent=False)


@mcp.tool()
async def change_card_pin(
    card_id: str,
    current_pin: str,
    new_pin: str,
) -> str:
    """
    Change the PIN on a card after verifying the current one.

    Args:
        card_id: The UUID of the card.
        current_pin: The existing 4-digit PIN.
        new_pin: The new 4-digit PIN.
    """
    body: dict = {"current_pin": current_pin, "new_pin": new_pin}
    return await _put(f"/cards/{card_id}/pin", body)


@mcp.tool()
async def update_card_limit(
    card_id: str,
    amount: float,
    pin: str,
    limit_type: str = "daily",
) -> str:
    """
    Update the spending limit on a card.

    Args:
        card_id: The UUID of the card.
        amount: New limit amount in PKR.
        pin: The user's 4-digit PIN for verification.
        limit_type: Type of limit — 'daily', 'online', or 'atm'.
    """
    body: dict = {"amount": amount, "limit_type": limit_type, "pin": pin}
    return await _put(f"/cards/{card_id}/limit", body)


# ── Analytics ─────────────────────────────────────────────────

@mcp.tool()
async def get_spending_analytics(
    period: str = "last_month",
    category: Optional[str] = None,
) -> str:
    """
    Get spending insights and category breakdown.

    Args:
        period: Time range — 'last_week', 'last_month', or 'last_3_months'.
        category: Optional filter by transaction type (e.g. 'TRANSFER').
    """
    params: dict = {"period": period}
    if category:
        params["category"] = category
    return await _get("/analytics/spend", params)


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    mcp.run()
