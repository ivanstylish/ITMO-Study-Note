package util;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

public class Event {
    private static final List<Runnable> listeners = new ArrayList<>();
    private static final Map<Class<?>, List<Consumer<?>>> runner = new HashMap<>();

    public static void publish() {
        listeners.forEach(Runnable::run);
    }

    public static <T> void subscribe(Class<T> eventType, Consumer<T> listener) {
        runner.computeIfAbsent(eventType, k -> new ArrayList<>()).add(listener);
    }

    public static <T> void publish(T event) {
        List<Consumer<?>> consumers = runner.get(event.getClass());
        if (consumers != null) {
            consumers.forEach(consumer -> ((Consumer<T>) consumer).accept(event));
        }
    }
}
