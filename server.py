#!/usr/bin/env python3
"""Agent Checkout MCP server — create Stripe payment links from any MCP client.

One tool: create_checkout_link. The agent finds the product; the human pays.
Reads AGENT_CHECKOUT_API_KEY from the environment (get one free at
https://checkout.ignitionfoundry.com — POST /v1/keys).
"""

import json
import os
import sys

BASE = "https://checkout.ignitionfoundry.com"
API_KEY = os.environ.get("AGENT_CHECKOUT_API_KEY", "")


def _http(method, path, body=None):
    import urllib.request
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "agent-checkout-mcp/1.0",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except Exception as e:
        # urllib raises HTTPError (a response) on 4xx/5xx
        if hasattr(e, "read"):
            try:
                return e.code, json.loads(e.read())
            except Exception:
                pass
        raise RuntimeError(f"request failed: {e}")


def create_checkout_link(amount_cents: int, product_name: str,
                         currency: str = "usd", description: str = "") -> dict:
    """Create a Stripe payment link your operator can click to pay.

    Use when your human wants to buy something and you need a checkout URL.
    You find the product and price; this returns a payment link you hand to
    your operator. They complete the payment — you never touch card data.

    Args:
        amount_cents: price in cents, 50 to 500000 ($0.50-$5,000)
        product_name: what they're buying (2-100 chars, shown to payer)
        currency: 3-letter code, default "usd"
        description: optional extra detail (max 500 chars)
    """
    if not API_KEY:
        raise RuntimeError(
            "Set AGENT_CHECKOUT_API_KEY first (free at "
            f"{BASE} — POST /v1/keys)."
        )
    status, data = _http("POST", "/v1/checkout-links", {
        "amount_cents": amount_cents,
        "currency": currency,
        "product_name": product_name,
        "description": description,
    })
    if status >= 400:
        raise RuntimeError(data.get("error", f"HTTP {status}"))
    return data


def check_link_status(link_id: str) -> dict:
    """Check whether a previously created payment link has been paid."""
    if not API_KEY:
        raise RuntimeError("Set AGENT_CHECKOUT_API_KEY first.")
    status, data = _http("GET", f"/v1/links/{link_id}")
    if status >= 400:
        raise RuntimeError(data.get("error", f"HTTP {status}"))
    return data


TOOLS = {
    "create_checkout_link": {
        "description": create_checkout_link.__doc__.split("\n\n")[0],
        "inputSchema": {
            "type": "object",
            "properties": {
                "amount_cents": {"type": "integer", "minimum": 50, "maximum": 500000,
                                "description": "Price in cents ($0.50-$5,000)"},
                "product_name": {"type": "string", "minLength": 2, "maxLength": 100,
                                "description": "What the operator is buying"},
                "currency": {"type": "string", "default": "usd",
                             "description": "3-letter currency code"},
                "description": {"type": "string", "maxLength": 500,
                               "description": "Optional detail shown to payer"},
            },
            "required": ["amount_cents", "product_name"],
        },
    },
    "check_link_status": {
        "description": "Check whether a payment link has been paid yet.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "link_id": {"type": "string",
                            "description": "The link_id from create_checkout_link"},
            },
            "required": ["link_id"],
        },
    },
}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        mid = msg.get("id")
        method = msg.get("method")

        def reply(result=None, error=None):
            out = {"jsonrpc": "2.0", "id": mid}
            if error is not None:
                out["error"] = {"code": -32000, "message": str(error)}
            else:
                out["result"] = result
            sys.stdout.write(json.dumps(out) + "\n")
            sys.stdout.flush()

        if method == "initialize":
            reply({"protocolVersion": "2024-11-05",
                   "capabilities": {"tools": {}},
                   "serverInfo": {"name": "agent-checkout", "version": "1.0.0"}})
        elif method == "ping":
            reply({})
        elif method == "tools/list":
            reply({"tools": [
                {"name": n, **spec} for n, spec in TOOLS.items()
            ]})
        elif method == "resources/list":
            reply({"resources": []})
        elif method == "prompts/list":
            reply({"prompts": []})
        elif method == "tools/call":
            name = msg.get("params", {}).get("name")
            args = msg.get("params", {}).get("arguments", {}) or {}
            try:
                if name == "create_checkout_link":
                    result = create_checkout_link(**args)
                elif name == "check_link_status":
                    result = check_link_status(**args)
                else:
                    raise RuntimeError(f"unknown tool: {name}")
                reply({"content": [{"type": "text",
                                     "text": json.dumps(result, indent=2)}]})
            except TypeError as e:
                reply(error=f"bad arguments: {e}")
            except Exception as e:
                reply(error=str(e))
        elif method and method.startswith("notifications/"):
            continue
        elif mid is None:
            continue
        else:
            reply(error=f"unknown method: {method}")


if __name__ == "__main__":
    main()
