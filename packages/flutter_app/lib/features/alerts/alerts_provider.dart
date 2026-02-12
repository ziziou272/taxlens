import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/models/alert.dart';

final alertsProvider = Provider<List<Alert>>((ref) {
  return const [
    Alert(
      id: '1',
      title: 'Estimated tax underpayment',
      description:
          'You may owe \$12,630 at filing. Consider increasing withholding or making estimated payments.',
      priority: AlertPriority.critical,
    ),
    Alert(
      id: '2',
      title: 'RSU vesting tax impact',
      description:
          'Your RSU vesting pushed you into the 32% bracket. Supplemental withholding may be insufficient.',
      priority: AlertPriority.critical,
    ),
    Alert(
      id: '3',
      title: 'Capital gains harvesting opportunity',
      description:
          'You have unrealized losses that could offset \$8,200 in capital gains.',
      priority: AlertPriority.warning,
    ),
    Alert(
      id: '4',
      title: 'State tax nexus',
      description: 'Remote work in multiple states may create filing obligations.',
      priority: AlertPriority.warning,
    ),
    Alert(
      id: '5',
      title: '401(k) contribution room',
      description: 'You have \$4,500 remaining in 401(k) contribution room for 2024.',
      priority: AlertPriority.info,
    ),
  ];
});
