package br.edu.devsecops;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class TaskApiTest {
    @Autowired MockMvc mvc;
    @Autowired ObjectMapper json;

    @Test void healthAndSecurityHeaders() throws Exception {
        mvc.perform(get("/api/health")).andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("UP"))
                .andExpect(header().string("X-Content-Type-Options", "nosniff"))
                .andExpect(header().string("X-Frame-Options", "DENY"))
                .andExpect(header().string("Cross-Origin-Resource-Policy", "same-origin"))
                .andExpect(header().string("Cache-Control", "no-store"))
                .andExpect(header().string("Referrer-Policy", "no-referrer"));
    }

    @Test void taskLifecycle() throws Exception {
        String result = mvc.perform(post("/api/tasks").contentType("application/json")
                .content("{\"title\":\"  Pipeline  \",\"description\":\"Testar gates\"}"))
                .andExpect(status().isCreated()).andExpect(jsonPath("$.title").value("Pipeline"))
                .andReturn().getResponse().getContentAsString();
        JsonNode task = json.readTree(result);
        String path = "/api/tasks/" + task.get("id").asText();
        mvc.perform(get(path)).andExpect(status().isOk());
        mvc.perform(get("/api/tasks")).andExpect(status().isOk()).andExpect(jsonPath("$[0].id").exists());
        mvc.perform(delete(path)).andExpect(status().isNoContent());
        mvc.perform(get(path)).andExpect(status().isNotFound());
        mvc.perform(delete(path)).andExpect(status().isNotFound());
    }

    @Test void invalidInputsAndErrorsDoNotLeakStack() throws Exception {
        for (String body : new String[]{"{}", "{\"title\":\"  \"}", "{", "{\"title\":\"ok\",\"unexpected\":1}"}) {
            mvc.perform(post("/api/tasks").contentType("application/json").content(body))
                    .andExpect(status().isBadRequest()).andExpect(jsonPath("$.trace").doesNotExist());
        }
        mvc.perform(get("/api/tasks/not-a-uuid")).andExpect(status().isBadRequest());
        mvc.perform(post("/api/tasks").contentType("application/json")
                .content(json.writeValueAsString(java.util.Map.of("title", "x".repeat(161)))))
                .andExpect(status().isBadRequest());
        mvc.perform(post("/api/tasks").contentType("application/json")
                .content(json.writeValueAsString(java.util.Map.of("title", "ok", "description", "x".repeat(1025)))))
                .andExpect(status().isBadRequest());
    }
}
