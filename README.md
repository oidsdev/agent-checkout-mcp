# agent-checkout-mcp

<!-- mcp-name: io.github.oidsdev/agent-checkout-mcp -->

An MCP server for [Agent Checkout™](https://checkout.ignitionfoundry.com) — create real Stripe payment links from any MCP client.

The problem it solves: AI agents can't buy things. They have no wallet and no checkout flow. This server gives your agent one tool call that mints a real Stripe payment link. The agent hands the URL to its human operator, the human clicks and pays, and the agent never touches card data.

## Tools

- **create_checkout_link** — mint a Stripe payment link (`amount_cents`, `product_name`, optional `currency`, `description`). Returns the checkout URL to hand to your operator.
- **check_link_status** — check whether a previously created link has been paid.

## Setup

No dependencies. Python 3.9+.

```bash
export AGENT_CHECKOUT_API_KEY="your-key"   # free at https://checkout.ignitionfoundry.com — POST /v1/keys
```

Add to your MCP client config (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "agent-checkout": {
      "command": "python3",
      "args": ["/path/to/server.py"],
      "env": { "AGENT_CHECKOUT_API_KEY": "your-key" }
    }
  }
}
```

Free tier: 100 links/day, no card required.

## How the money flows

1. Your agent calls `create_checkout_link` with a price and product name.
2. The server returns a Stripe payment link.
3. The agent shows the link to its operator.
4. The operator pays on Stripe's hosted page. Funds settle directly to the merchant.
5. The agent can poll `check_link_status` to confirm payment.

The agent never sees card numbers, and the merchant's Stripe account is the merchant of record.

## License

MIT — Orbital Desk LLC.
