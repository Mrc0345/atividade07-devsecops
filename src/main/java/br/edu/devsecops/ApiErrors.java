package br.edu.devsecops;

import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.server.ResponseStatusException;

@RestControllerAdvice
public class ApiErrors {
    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class,
            MethodArgumentTypeMismatchException.class})
    ProblemDetail invalidInput(Exception ignored) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, "Entrada invalida: verifique formato e limites dos campos");
    }

    @ExceptionHandler(ResponseStatusException.class)
    ProblemDetail knownError(ResponseStatusException error) {
        return ProblemDetail.forStatusAndDetail(error.getStatusCode(), error.getReason());
    }
}
