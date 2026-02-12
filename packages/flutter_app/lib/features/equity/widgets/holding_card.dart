import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';
import '../equity_provider.dart';

class HoldingCard extends StatelessWidget {
  const HoldingCard({super.key, required this.holding, this.onTap});
  final Holding holding;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat.currency(symbol: '\$');
    final gain = holding.unrealizedGain;
    final gainColor = gain >= 0 ? AppColors.positive : AppColors.negative;
    final gainPrefix = gain >= 0 ? '+' : '';

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        onTap: onTap,
        leading: CircleAvatar(
          backgroundColor: AppColors.brand.withAlpha(30),
          child: Text(holding.symbol.substring(0, 2),
              style: TextStyle(
                  color: AppColors.brand, fontWeight: FontWeight.bold)),
        ),
        title: Text('${holding.symbol} • ${holding.totalShares} shares'),
        subtitle: Text(fmt.format(holding.currentValue),
            style: const TextStyle(fontSize: 13)),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text('$gainPrefix${fmt.format(gain)}',
                style: TextStyle(
                    color: gainColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 14)),
            Text(holding.grantTypeLabel,
                style: TextStyle(
                    color: AppColors.textSecondary, fontSize: 11)),
          ],
        ),
      ),
    );
  }
}
