import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';
import '../equity_provider.dart';

class TaxLotRow extends StatelessWidget {
  const TaxLotRow({super.key, required this.lot});
  final TaxLot lot;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat.currency(symbol: '\$');
    final dateFmt = DateFormat.yMMMd();
    final gain = lot.gainLoss;
    final gainColor = gain >= 0 ? AppColors.positive : AppColors.negative;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('${lot.shares} shares',
                  style: const TextStyle(fontWeight: FontWeight.w500)),
              Text('${gain >= 0 ? '+' : ''}${fmt.format(gain)}',
                  style: TextStyle(
                      color: gainColor, fontWeight: FontWeight.w600)),
            ],
          ),
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Acquired ${dateFmt.format(lot.dateAcquired)}',
                  style: TextStyle(
                      color: AppColors.textSecondary, fontSize: 12)),
              Text('Basis: ${fmt.format(lot.costBasis)}',
                  style: TextStyle(
                      color: AppColors.textSecondary, fontSize: 12)),
            ],
          ),
        ],
      ),
    );
  }
}
