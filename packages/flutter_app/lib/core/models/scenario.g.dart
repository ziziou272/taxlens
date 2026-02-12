// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'scenario.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ScenarioImpl _$$ScenarioImplFromJson(Map<String, dynamic> json) =>
    _$ScenarioImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      type: json['type'] as String,
      currentTax: (json['currentTax'] as num).toDouble(),
      projectedTax: (json['projectedTax'] as num).toDouble(),
      savings: (json['savings'] as num).toDouble(),
      parameters: json['parameters'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$ScenarioImplToJson(_$ScenarioImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'type': instance.type,
      'currentTax': instance.currentTax,
      'projectedTax': instance.projectedTax,
      'savings': instance.savings,
      'parameters': instance.parameters,
    };
