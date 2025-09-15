# Subscription System Documentation

## Overview

The bot now includes a comprehensive subscription system that allows users to purchase premium subscriptions with different durations. The system integrates with YooKassa payment gateway for secure payment processing.

## Features

### User Features
- **Subscription Button**: Available in user profile menu for easy access
- **4 Subscription Tiers**: 1 month, 3 months, 6 months, and 1 year options
- **Automatic Extension**: If user has existing subscription, new purchases extend the current subscription period
- **Status Tracking**: Users can view their current subscription status, expiration date, and remaining days
- **Secure Payments**: Integration with YooKassa test payment gateway

### Technical Features
- **Database Integration**: Separate `subscriptions` table for storing subscription data
- **Payment Tracking**: Each subscription linked to payment ID for audit trail
- **Expiration Management**: Automatic detection of expired subscriptions
- **Extension Logic**: Smart handling of subscription renewals and extensions

## Subscription Tiers

| Duration | Price | Days | Description |
|----------|--------|------|-------------|
| 1 месяц | 299₽ | 30 | Monthly subscription |
| 3 месяца | 799₽ | 90 | Quarterly subscription (Best value) |
| 6 месяцев | 1499₽ | 180 | Semi-annual subscription |
| 1 год | 2799₽ | 365 | Annual subscription (Maximum savings) |

## User Workflow

1. **Access Subscription**: User clicks "💎 Подписка" button in profile menu
2. **View Options**: Bot displays subscription tiers with pricing
3. **Select Period**: User chooses desired subscription duration
4. **Payment**: User is redirected to YooKassa payment page
5. **Activation**: Upon successful payment, subscription is automatically activated
6. **Management**: User can extend existing subscriptions or view status

## Database Schema

### Subscriptions Table
```sql
CREATE TABLE subscriptions (
    telegram_id INTEGER PRIMARY KEY,
    subscription_type TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    payment_id TEXT,
    amount REAL,
    currency TEXT DEFAULT 'RUB',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
```

## API Integration

### YooKassa Configuration
- **Test Shop ID**: `1000000`
- **Test Secret Key**: `test_secretkey`
- **API Endpoint**: `https://api.yookassa.ru/v3`
- **Currency**: RUB (Russian Rubles)

### Payment Flow
1. Create payment request with subscription metadata
2. Redirect user to YooKassa payment page
3. Monitor payment status via polling
4. Process successful payments and activate subscriptions
5. Handle payment failures gracefully

## Code Components

### Models
- `models/subscription.py`: Subscription data model with expiration logic
- Database operations in `database.py` for subscription management

### Services
- `payment_service.py`: YooKassa integration and payment processing
- Pricing configuration and payment creation/verification

### User Interface
- `keyboards.py`: Subscription-related keyboards and buttons
- `handlers.py`: Message and callback handlers for subscription flow
- `message_generator.py`: Subscription menu generation and status display

### Key Methods
- `handle_subscription_menu()`: Display subscription options
- `handle_subscription_period_selection()`: Process period selection and create payment
- `extend_subscription()`: Extend existing subscription duration
- `get_subscription()`: Retrieve user's current subscription status

## Configuration

The subscription system uses the existing bot configuration. No additional environment variables are required for basic functionality.

For production deployment, consider:
- Updating YooKassa credentials to production values
- Implementing webhook receivers for real-time payment notifications
- Adding subscription benefits and feature gating
- Setting up automated expiration notifications

## Testing

The implementation includes comprehensive test coverage:
- Unit tests for subscription model
- Database operation tests
- Payment service integration tests
- UI component validation
- End-to-end workflow simulation

Run tests with:
```bash
python test_subscription_system.py
python demo_subscription.py
```

## Security Considerations

- Payment data is handled securely through YooKassa
- No sensitive payment information stored locally
- Payment IDs used for transaction tracking and audit
- User authentication via Telegram ID

## Future Enhancements

Potential improvements for the subscription system:
- Webhook integration for real-time payment notifications
- Subscription benefits and premium features
- Automated renewal reminders
- Usage analytics and reporting
- Discount codes and promotional pricing
- Family/group subscription plans