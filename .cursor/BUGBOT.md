# Bugbot review rules — Agent Checkout (oidsdev/agent-checkout-mcp)

Payment-link generation for AI agents via Stripe Connect. Money moves here,
so the review bar is the highest in the org.

## Blocking (must flag)

- **No real Stripe keys anywhere.** Test keys only (`sk_test_`, `pk_test_`),
  and only in clearly-marked test fixtures. Flag any `sk_live_` or
  production key, even in comments.
- **Amounts must be explicit and validated.** Flag any payment-amount
  calculation that doesn't validate currency, rounding, or minimums.
- **No silent money movement.** Every charge, refund, or transfer must be
  logged with amount, currency, and both parties. Flag unlogged money ops.
- **Idempotency on all payment operations.** Flag any Stripe call without an
  idempotency key where retries are possible.
- **Webhook signatures must be verified.** Flag any webhook handler that
  processes events without verifying the Stripe signature.
- **No PII in logs.** Flag logging of card numbers, full emails, or
  bank details.

## Non-blocking (suggest)

- Copy must be brief and human. No em dashes.
- Error messages to end users should not leak implementation details.

## Context

- The merchant/customer model: the agent works for a merchant selling their
  own goods; the customer pays via Stripe; funds settle to the merchant's
  connected account. Flag anything that contradicts this model.
