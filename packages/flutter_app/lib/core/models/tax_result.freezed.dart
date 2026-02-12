// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'tax_result.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

TaxResult _$TaxResultFromJson(Map<String, dynamic> json) {
  return _TaxResult.fromJson(json);
}

/// @nodoc
mixin _$TaxResult {
  double get totalIncome => throw _privateConstructorUsedError;
  double get federalTax => throw _privateConstructorUsedError;
  double get stateTax => throw _privateConstructorUsedError;
  double get totalTax => throw _privateConstructorUsedError;
  double get effectiveRate => throw _privateConstructorUsedError;
  double get marginalRate => throw _privateConstructorUsedError;
  double get totalWithheld => throw _privateConstructorUsedError;
  double get amountOwed => throw _privateConstructorUsedError;
  Map<String, double> get incomeBreakdown => throw _privateConstructorUsedError;
  double get taxableIncome => throw _privateConstructorUsedError;
  double get deductionUsed => throw _privateConstructorUsedError;
  double get socialSecurityTax => throw _privateConstructorUsedError;
  double get medicareTax => throw _privateConstructorUsedError;

  /// Serializes this TaxResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of TaxResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $TaxResultCopyWith<TaxResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TaxResultCopyWith<$Res> {
  factory $TaxResultCopyWith(TaxResult value, $Res Function(TaxResult) then) =
      _$TaxResultCopyWithImpl<$Res, TaxResult>;
  @useResult
  $Res call(
      {double totalIncome,
      double federalTax,
      double stateTax,
      double totalTax,
      double effectiveRate,
      double marginalRate,
      double totalWithheld,
      double amountOwed,
      Map<String, double> incomeBreakdown,
      double taxableIncome,
      double deductionUsed,
      double socialSecurityTax,
      double medicareTax});
}

/// @nodoc
class _$TaxResultCopyWithImpl<$Res, $Val extends TaxResult>
    implements $TaxResultCopyWith<$Res> {
  _$TaxResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of TaxResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalIncome = null,
    Object? federalTax = null,
    Object? stateTax = null,
    Object? totalTax = null,
    Object? effectiveRate = null,
    Object? marginalRate = null,
    Object? totalWithheld = null,
    Object? amountOwed = null,
    Object? incomeBreakdown = null,
    Object? taxableIncome = null,
    Object? deductionUsed = null,
    Object? socialSecurityTax = null,
    Object? medicareTax = null,
  }) {
    return _then(_value.copyWith(
      totalIncome: null == totalIncome
          ? _value.totalIncome
          : totalIncome // ignore: cast_nullable_to_non_nullable
              as double,
      federalTax: null == federalTax
          ? _value.federalTax
          : federalTax // ignore: cast_nullable_to_non_nullable
              as double,
      stateTax: null == stateTax
          ? _value.stateTax
          : stateTax // ignore: cast_nullable_to_non_nullable
              as double,
      totalTax: null == totalTax
          ? _value.totalTax
          : totalTax // ignore: cast_nullable_to_non_nullable
              as double,
      effectiveRate: null == effectiveRate
          ? _value.effectiveRate
          : effectiveRate // ignore: cast_nullable_to_non_nullable
              as double,
      marginalRate: null == marginalRate
          ? _value.marginalRate
          : marginalRate // ignore: cast_nullable_to_non_nullable
              as double,
      totalWithheld: null == totalWithheld
          ? _value.totalWithheld
          : totalWithheld // ignore: cast_nullable_to_non_nullable
              as double,
      amountOwed: null == amountOwed
          ? _value.amountOwed
          : amountOwed // ignore: cast_nullable_to_non_nullable
              as double,
      incomeBreakdown: null == incomeBreakdown
          ? _value.incomeBreakdown
          : incomeBreakdown // ignore: cast_nullable_to_non_nullable
              as Map<String, double>,
      taxableIncome: null == taxableIncome
          ? _value.taxableIncome
          : taxableIncome // ignore: cast_nullable_to_non_nullable
              as double,
      deductionUsed: null == deductionUsed
          ? _value.deductionUsed
          : deductionUsed // ignore: cast_nullable_to_non_nullable
              as double,
      socialSecurityTax: null == socialSecurityTax
          ? _value.socialSecurityTax
          : socialSecurityTax // ignore: cast_nullable_to_non_nullable
              as double,
      medicareTax: null == medicareTax
          ? _value.medicareTax
          : medicareTax // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$TaxResultImplCopyWith<$Res>
    implements $TaxResultCopyWith<$Res> {
  factory _$$TaxResultImplCopyWith(
          _$TaxResultImpl value, $Res Function(_$TaxResultImpl) then) =
      __$$TaxResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {double totalIncome,
      double federalTax,
      double stateTax,
      double totalTax,
      double effectiveRate,
      double marginalRate,
      double totalWithheld,
      double amountOwed,
      Map<String, double> incomeBreakdown,
      double taxableIncome,
      double deductionUsed,
      double socialSecurityTax,
      double medicareTax});
}

/// @nodoc
class __$$TaxResultImplCopyWithImpl<$Res>
    extends _$TaxResultCopyWithImpl<$Res, _$TaxResultImpl>
    implements _$$TaxResultImplCopyWith<$Res> {
  __$$TaxResultImplCopyWithImpl(
      _$TaxResultImpl _value, $Res Function(_$TaxResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of TaxResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalIncome = null,
    Object? federalTax = null,
    Object? stateTax = null,
    Object? totalTax = null,
    Object? effectiveRate = null,
    Object? marginalRate = null,
    Object? totalWithheld = null,
    Object? amountOwed = null,
    Object? incomeBreakdown = null,
    Object? taxableIncome = null,
    Object? deductionUsed = null,
    Object? socialSecurityTax = null,
    Object? medicareTax = null,
  }) {
    return _then(_$TaxResultImpl(
      totalIncome: null == totalIncome
          ? _value.totalIncome
          : totalIncome // ignore: cast_nullable_to_non_nullable
              as double,
      federalTax: null == federalTax
          ? _value.federalTax
          : federalTax // ignore: cast_nullable_to_non_nullable
              as double,
      stateTax: null == stateTax
          ? _value.stateTax
          : stateTax // ignore: cast_nullable_to_non_nullable
              as double,
      totalTax: null == totalTax
          ? _value.totalTax
          : totalTax // ignore: cast_nullable_to_non_nullable
              as double,
      effectiveRate: null == effectiveRate
          ? _value.effectiveRate
          : effectiveRate // ignore: cast_nullable_to_non_nullable
              as double,
      marginalRate: null == marginalRate
          ? _value.marginalRate
          : marginalRate // ignore: cast_nullable_to_non_nullable
              as double,
      totalWithheld: null == totalWithheld
          ? _value.totalWithheld
          : totalWithheld // ignore: cast_nullable_to_non_nullable
              as double,
      amountOwed: null == amountOwed
          ? _value.amountOwed
          : amountOwed // ignore: cast_nullable_to_non_nullable
              as double,
      incomeBreakdown: null == incomeBreakdown
          ? _value._incomeBreakdown
          : incomeBreakdown // ignore: cast_nullable_to_non_nullable
              as Map<String, double>,
      taxableIncome: null == taxableIncome
          ? _value.taxableIncome
          : taxableIncome // ignore: cast_nullable_to_non_nullable
              as double,
      deductionUsed: null == deductionUsed
          ? _value.deductionUsed
          : deductionUsed // ignore: cast_nullable_to_non_nullable
              as double,
      socialSecurityTax: null == socialSecurityTax
          ? _value.socialSecurityTax
          : socialSecurityTax // ignore: cast_nullable_to_non_nullable
              as double,
      medicareTax: null == medicareTax
          ? _value.medicareTax
          : medicareTax // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$TaxResultImpl implements _TaxResult {
  const _$TaxResultImpl(
      {required this.totalIncome,
      required this.federalTax,
      required this.stateTax,
      required this.totalTax,
      required this.effectiveRate,
      required this.marginalRate,
      required this.totalWithheld,
      required this.amountOwed,
      required final Map<String, double> incomeBreakdown,
      this.taxableIncome = 0,
      this.deductionUsed = 0,
      this.socialSecurityTax = 0,
      this.medicareTax = 0})
      : _incomeBreakdown = incomeBreakdown;

  factory _$TaxResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$TaxResultImplFromJson(json);

  @override
  final double totalIncome;
  @override
  final double federalTax;
  @override
  final double stateTax;
  @override
  final double totalTax;
  @override
  final double effectiveRate;
  @override
  final double marginalRate;
  @override
  final double totalWithheld;
  @override
  final double amountOwed;
  final Map<String, double> _incomeBreakdown;
  @override
  Map<String, double> get incomeBreakdown {
    if (_incomeBreakdown is EqualUnmodifiableMapView) return _incomeBreakdown;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_incomeBreakdown);
  }

  @override
  @JsonKey()
  final double taxableIncome;
  @override
  @JsonKey()
  final double deductionUsed;
  @override
  @JsonKey()
  final double socialSecurityTax;
  @override
  @JsonKey()
  final double medicareTax;

  @override
  String toString() {
    return 'TaxResult(totalIncome: $totalIncome, federalTax: $federalTax, stateTax: $stateTax, totalTax: $totalTax, effectiveRate: $effectiveRate, marginalRate: $marginalRate, totalWithheld: $totalWithheld, amountOwed: $amountOwed, incomeBreakdown: $incomeBreakdown, taxableIncome: $taxableIncome, deductionUsed: $deductionUsed, socialSecurityTax: $socialSecurityTax, medicareTax: $medicareTax)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TaxResultImpl &&
            (identical(other.totalIncome, totalIncome) ||
                other.totalIncome == totalIncome) &&
            (identical(other.federalTax, federalTax) ||
                other.federalTax == federalTax) &&
            (identical(other.stateTax, stateTax) ||
                other.stateTax == stateTax) &&
            (identical(other.totalTax, totalTax) ||
                other.totalTax == totalTax) &&
            (identical(other.effectiveRate, effectiveRate) ||
                other.effectiveRate == effectiveRate) &&
            (identical(other.marginalRate, marginalRate) ||
                other.marginalRate == marginalRate) &&
            (identical(other.totalWithheld, totalWithheld) ||
                other.totalWithheld == totalWithheld) &&
            (identical(other.amountOwed, amountOwed) ||
                other.amountOwed == amountOwed) &&
            const DeepCollectionEquality()
                .equals(other._incomeBreakdown, _incomeBreakdown) &&
            (identical(other.taxableIncome, taxableIncome) ||
                other.taxableIncome == taxableIncome) &&
            (identical(other.deductionUsed, deductionUsed) ||
                other.deductionUsed == deductionUsed) &&
            (identical(other.socialSecurityTax, socialSecurityTax) ||
                other.socialSecurityTax == socialSecurityTax) &&
            (identical(other.medicareTax, medicareTax) ||
                other.medicareTax == medicareTax));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      totalIncome,
      federalTax,
      stateTax,
      totalTax,
      effectiveRate,
      marginalRate,
      totalWithheld,
      amountOwed,
      const DeepCollectionEquality().hash(_incomeBreakdown),
      taxableIncome,
      deductionUsed,
      socialSecurityTax,
      medicareTax);

  /// Create a copy of TaxResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$TaxResultImplCopyWith<_$TaxResultImpl> get copyWith =>
      __$$TaxResultImplCopyWithImpl<_$TaxResultImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$TaxResultImplToJson(
      this,
    );
  }
}

abstract class _TaxResult implements TaxResult {
  const factory _TaxResult(
      {required final double totalIncome,
      required final double federalTax,
      required final double stateTax,
      required final double totalTax,
      required final double effectiveRate,
      required final double marginalRate,
      required final double totalWithheld,
      required final double amountOwed,
      required final Map<String, double> incomeBreakdown,
      final double taxableIncome,
      final double deductionUsed,
      final double socialSecurityTax,
      final double medicareTax}) = _$TaxResultImpl;

  factory _TaxResult.fromJson(Map<String, dynamic> json) =
      _$TaxResultImpl.fromJson;

  @override
  double get totalIncome;
  @override
  double get federalTax;
  @override
  double get stateTax;
  @override
  double get totalTax;
  @override
  double get effectiveRate;
  @override
  double get marginalRate;
  @override
  double get totalWithheld;
  @override
  double get amountOwed;
  @override
  Map<String, double> get incomeBreakdown;
  @override
  double get taxableIncome;
  @override
  double get deductionUsed;
  @override
  double get socialSecurityTax;
  @override
  double get medicareTax;

  /// Create a copy of TaxResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$TaxResultImplCopyWith<_$TaxResultImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
