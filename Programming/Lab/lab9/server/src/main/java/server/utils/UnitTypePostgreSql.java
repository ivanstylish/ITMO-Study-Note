package server.utils;

import common.model.UnitOfMeasure;
import org.hibernate.HibernateException;
import org.hibernate.engine.spi.SharedSessionContractImplementor;
import org.hibernate.usertype.UserType;

import java.io.Serializable;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.util.Objects;

public class UnitTypePostgreSql implements UserType<UnitOfMeasure> {

  @Override
  public UnitOfMeasure replace(UnitOfMeasure original, UnitOfMeasure target, Object owner) throws HibernateException {
    return original;
  }
  @Override
  public int getSqlType() {
    return Types.OTHER; // 使用 Types.OTHER 映射 PostgreSQL 枚举
  }

  @Override
  public Class<UnitOfMeasure> returnedClass() {
    return UnitOfMeasure.class;
  }

  @Override
  public boolean equals(UnitOfMeasure x, UnitOfMeasure y) throws HibernateException {
    return Objects.equals(x, y);
  }

  @Override
  public int hashCode(UnitOfMeasure x) throws HibernateException {
    return x == null ? 0 : x.hashCode();
  }

  @Override
  public UnitOfMeasure nullSafeGet(
    ResultSet rs,
    int position,
    SharedSessionContractImplementor session,
    Object owner
  ) throws SQLException {
    String value = rs.getString(position);
    return value == null ? null : UnitOfMeasure.valueOf(value);
  }

  @Override
  public void nullSafeSet(
    PreparedStatement st,
    UnitOfMeasure value,
    int index,
    SharedSessionContractImplementor session
  ) throws SQLException {
    if (value == null) {
      st.setNull(index, Types.OTHER);
    } else {
      st.setObject(index, value.name(), Types.OTHER); // 使用枚举名称
    }
  }

  @Override
  public UnitOfMeasure deepCopy(UnitOfMeasure value) throws HibernateException {
    return value; // 枚举不可变，直接返回
  }

  @Override
  public boolean isMutable() {
    return false; // 枚举不可变
  }

  @Override
  public Serializable disassemble(UnitOfMeasure value) throws HibernateException {
    return value.name();
  }

  @Override
  public UnitOfMeasure assemble(Serializable cached, Object owner) throws HibernateException {
    return UnitOfMeasure.valueOf((String) cached);
  }
}

