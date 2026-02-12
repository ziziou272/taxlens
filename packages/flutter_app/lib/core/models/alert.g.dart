// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'alert.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$AlertImpl _$$AlertImplFromJson(Map<String, dynamic> json) => _$AlertImpl(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      priority: $enumDecode(_$AlertPriorityEnumMap, json['priority']),
      dismissed: json['dismissed'] as bool? ?? false,
    );

Map<String, dynamic> _$$AlertImplToJson(_$AlertImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'description': instance.description,
      'priority': _$AlertPriorityEnumMap[instance.priority]!,
      'dismissed': instance.dismissed,
    };

const _$AlertPriorityEnumMap = {
  AlertPriority.critical: 'critical',
  AlertPriority.warning: 'warning',
  AlertPriority.info: 'info',
};
