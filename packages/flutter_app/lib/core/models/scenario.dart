import 'package:freezed_annotation/freezed_annotation.dart';

part 'scenario.freezed.dart';
part 'scenario.g.dart';

@freezed
class Scenario with _$Scenario {
  const factory Scenario({
    required String id,
    required String name,
    required String type,
    required double currentTax,
    required double projectedTax,
    required double savings,
    Map<String, dynamic>? parameters,
  }) = _Scenario;

  factory Scenario.fromJson(Map<String, dynamic> json) =>
      _$ScenarioFromJson(json);
}
