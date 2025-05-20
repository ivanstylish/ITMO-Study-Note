package common.network.requests;

import common.user.User;
import common.utility.Commands;

public class MaxByCreationDateRequest extends Request{
  public MaxByCreationDateRequest(User user){
    super(Commands.MAX_BY_CREATION_DATE, user);
  }
}
