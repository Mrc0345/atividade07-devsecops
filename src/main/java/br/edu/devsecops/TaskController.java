package br.edu.devsecops;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.net.URI;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api")
public class TaskController {
    private final Map<UUID, Task> tasks = new ConcurrentHashMap<>();
    private static final int MAX_TASKS = 1000;

    public record Task(UUID id, String title, String description) {}
    public record NewTask(@NotBlank @Size(max = 160) String title,
                          @Size(max = 1024) String description) {}

    @GetMapping("/health")
    public Map<String, String> health() { return Map.of("status", "UP"); }

    @GetMapping("/tasks")
    public List<Task> list() {
        return tasks.values().stream().sorted(Comparator.comparing(Task::id)).toList();
    }

    @PostMapping("/tasks")
    public synchronized ResponseEntity<Task> create(@Valid @RequestBody NewTask input) {
        if (tasks.size() >= MAX_TASKS) {
            throw new ResponseStatusException(HttpStatus.TOO_MANY_REQUESTS, "Limite de tarefas atingido");
        }
        Task task = new Task(UUID.randomUUID(), input.title().strip(),
                input.description() == null ? "" : input.description().strip());
        tasks.put(task.id(), task);
        return ResponseEntity.created(URI.create("/api/tasks/" + task.id())).body(task);
    }

    @GetMapping("/tasks/{id}")
    public Task get(@PathVariable UUID id) {
        Task task = tasks.get(id);
        if (task == null) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Tarefa nao encontrada");
        return task;
    }

    @DeleteMapping("/tasks/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable UUID id) {
        if (tasks.remove(id) == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Tarefa nao encontrada");
        }
    }
}
