package Items;

import Interfaces.Storable;

public class Pocket implements Storable {
    @Override
    public String storable() {
        return "левый карман для зеркала";
    }
}
