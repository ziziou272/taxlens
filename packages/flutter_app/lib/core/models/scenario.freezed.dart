// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'scenario.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

Scenario _$ScenarioFromJson(Map<String, dynamic> json) {
  return _Scenario.fromJson(json);
}

/// @nodoc
mixin _$Scenario {
  String get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get type => throw _privateConstructorUsedError;
  double get currentTax => throw _privateConstructorUsedError;
  double get projectedTax => throw _privateConstructorUsedError;
  double get savings => throw _privateConstructorUsedError;
  Map<String, dynamic>? get parameters => throw _privateConstructorUsedError;

  /// Serializes this Scenario to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Scenario
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ScenarioCopyWith<Scenario> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ScenarioCopyWith<$Res> {
  factory $ScenarioCopyWith(Scenario value, $Res Function(Scenario) then) =
      _$ScenarioCopyWithImpl<$Res, Scenario>;
  @useResult
  $Res call(
      {String id,
      String name,
      String type,
      double currentTax,
      double projectedTax,
      double savings,
      Map<String, dynamic>? parameters});
}

/// @nodoc
class _$ScenarioCopyWithImpl<$Res, $Val extends Scenario>
    implements $ScenarioCopyWith<$Res> {
  _$ScenarioCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Scenario
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? type = null,
    Object? currentTax = null,
    Object? projectedTax = null,
    Object? savings = null,
    Object? parameters = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      currentTax: null == currentTax
          ? _value.currentTax
          : currentTax // ignore: cast_nullable_to_non_nullable
              as double,
      projectedTax: null == projectedTax
          ? _value.projectedTax
          : projectedTax // ignore: cast_nullable_to_non_nullable
              as double,
      savings: null == savings
          ? _value.savings
          : savings // ignore: cast_nullable_to_non_nullable
              as double,
      parameters: freezed == parameters
          ? _value.parameters
          : parameters // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ScenarioImplCopyWith<$Res>
    implements $ScenarioCopyWith<$Res> {
  factory _$$ScenarioImplCopyWith(
          _$ScenarioImpl value, $Res Function(_$ScenarioImpl) then) =
      __$$ScenarioImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String type,
      double currentTax,
      double projectedTax,
      double savings,
      Map<String, dynamic>? parameters});
}

/// @nodoc
class __$$ScenarioImplCopyWithImpl<$Res>
    extends _$ScenarioCopyWithImpl<$Res, _$ScenarioImpl>
    implements _$$ScenarioImplCopyWith<$Res> {
  __$$ScenarioImplCopyWithImpl(
      _$ScenarioImpl _value, $Res Function(_$ScenarioImpl) _then)
      : super(_value, _then);

  /// Create a copy of Scenario
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? type = null,
    Object? currentTax = null,
    Object? projectedTax = null,
    Object? savings = null,
    Object? parameters = freezed,
  }) {
    return _then(_$ScenarioImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      currentTax: null == currentTax
          ? _value.currentTax
          : currentTax // ignore: cast_nullable_to_non_nullable
              as double,
      projectedTax: null == projectedTax
          ? _value.projectedTax
          : projectedTax // ignore: cast_nullable_to_non_nullable
              as double,
      savings: null == savings
          ? _value.savings
          : savings // ignore: cast_nullable_to_non_nullable
              as double,
      parameters: freezed == parameters
          ? _value._parameters
          : parameters // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ScenarioImpl implements _Scenario {
  const _$ScenarioImpl(
      {required this.id,
      required this.name,
      required this.type,
      required this.currentTax,
      required this.projectedTax,
      required this.savings,
      final Map<String, dynamic>? parameters})
      : _parameters = parameters;

  factory _$ScenarioImpl.fromJson(Map<String, dynamic> json) =>
      _$$ScenarioImplFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String type;
  @override
  final double currentTax;
  @override
  final double projectedTax;
  @override
  final double savings;
  final Map<String, dynamic>? _parameters;
  @override
  Map<String, dynamic>? get parameters {
    final value = _parameters;
    if (value == null) return null;
    if (_parameters is EqualUnmodifiableMapView) return _parameters;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'Scenario(id: $id, name: $name, type: $type, currentTax: $currentTax, projectedTax: $projectedTax, savings: $savings, parameters: $parameters)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ScenarioImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.currentTax, currentTax) ||
                other.currentTax == currentTax) &&
            (identical(other.projectedTax, projectedTax) ||
                other.projectedTax == projectedTax) &&
            (identical(other.savings, savings) || other.savings == savings) &&
            const DeepCollectionEquality()
                .equals(other._parameters, _parameters));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, name, type, currentTax,
      projectedTax, savings, const DeepCollectionEquality().hash(_parameters));

  /// Create a copy of Scenario
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ScenarioImplCopyWith<_$ScenarioImpl> get copyWith =>
      __$$ScenarioImplCopyWithImpl<_$ScenarioImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ScenarioImplToJson(
      this,
    );
  }
}

abstract class _Scenario implements Scenario {
  const factory _Scenario(
      {required final String id,
      required final String name,
      required final String type,
      required final double currentTax,
      required final double projectedTax,
      required final double savings,
      final Map<String, dynamic>? parameters}) = _$ScenarioImpl;

  factory _Scenario.fromJson(Map<String, dynamic> json) =
      _$ScenarioImpl.fromJson;

  @override
  String get id;
  @override
  String get name;
  @override
  String get type;
  @override
  double get currentTax;
  @override
  double get projectedTax;
  @override
  double get savings;
  @override
  Map<String, dynamic>? get parameters;

  /// Create a copy of Scenario
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ScenarioImplCopyWith<_$ScenarioImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
