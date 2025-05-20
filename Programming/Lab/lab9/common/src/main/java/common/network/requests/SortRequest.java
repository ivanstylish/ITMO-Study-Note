package common.network.requests;

import common.user.User;
import common.utility.Commands;

public class SortRequest extends Request{
  public SortRequest(User user){
    super(Commands.SORT, user);
  }
}
