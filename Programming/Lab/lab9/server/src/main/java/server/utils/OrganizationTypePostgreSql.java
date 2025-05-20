package server.utils;

import common.model.OrganizationType;
import org.hibernate.HibernateException;
import org.hibernate.engine.spi.SharedSessionContractImplementor;
import org.hibernate.usertype.UserType;

import java.io.Serializable;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.util.Objects;

public class OrganizationTypePostgreSql implements UserType<OrganizationType> {

  @Override
  public int getSqlType() {
    return Types.OTHER;
  }

  @Override
  public Class<OrganizationType> returnedClass() {
    return OrganizationType.class;
  }

  @Override
  public boolean equals(OrganizationType x, OrganizationType y) throws HibernateException {
    return Objects.equals(x, y);
  }

  @Override
  public int hashCode(OrganizationType x) throws HibernateException {
    return x == null ? 0 : x.hashCode();
  }

  @Override
  public OrganizationType nullSafeGet(
    ResultSet rs,
    int position,
    SharedSessionContractImplementor session,
    Object owner
  ) throws SQLException {
    String value = rs.getString(position);
    return value == null ? null : OrganizationType.valueOf(value);
  }

  @Override
  public void nullSafeSet(
    PreparedStatement st,
    OrganizationType value,
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
  public OrganizationType deepCopy(OrganizationType value) throws HibernateException {
    return value;
  }

  @Override
  public boolean isMutable() {
    return false;
  }

  @Override
  public Serializable disassemble(OrganizationType value) throws HibernateException {
    return value.name();
  }

  @Override
  public OrganizationType assemble(Serializable cached, Object owner) throws HibernateException {
    return OrganizationType.valueOf((String) cached);
  }

  @Override
  public OrganizationType replace(OrganizationType original, OrganizationType target, Object owner) throws HibernateException {
    return original;
  }
}
