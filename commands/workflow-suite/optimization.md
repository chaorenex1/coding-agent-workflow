---
description: Performance analysis and optimization recommendations with benchmarking
argument-hint: [component|function|endpoint]
allowed-tools: Read, Bash(find:*), Bash(grep:*), Bash(wc:*), Bash(du:*), Bash(time:*), Bash(node:*), Bash(python:*)
---

# Performance Optimization Assistant

## Context

Target for optimization: $ARGUMENTS

### Codebase Overview
!`find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" \) -not -path "*/node_modules/*" -not -path "*/.git/*" | wc -l`

### Large Files (Potential bottlenecks)
!`find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" \) -not -path "*/node_modules/*" -not -path "*/.git/*" -exec wc -l {} + 2>/dev/null | sort -rn | head -10`

### Performance-Critical Patterns
!`grep -r "async\|await\|Promise\|setTimeout\|setInterval\|loop\|for\|while" --include="*.js" --include="*.ts" --exclude-dir=node_modules --exclude-dir=.git . 2>/dev/null | wc -l`

## Your Task

Analyze and optimize performance for "$ARGUMENTS":

### 1. **Performance Profiling**

   **Current State Analysis:**
   - Measure current performance metrics
   - Identify bottlenecks
   - Analyze resource usage (CPU, memory, I/O)
   - Check for performance anti-patterns

   **Key Metrics:**
   - Response time: [Current]
   - Throughput: [Current]
   - Memory usage: [Current]
   - CPU usage: [Current]

### 2. **Bottleneck Identification**

   **Code-Level Bottlenecks:**
   - Inefficient algorithms (O(n²) → O(n log n))
   - Nested loops
   - Synchronous operations blocking async
   - Unnecessary computations

   **I/O Bottlenecks:**
   - Database query inefficiency
   - N+1 query problems
   - Unindexed queries
   - Large payload transfers

   **Memory Bottlenecks:**
   - Memory leaks
   - Large object retention
   - Inefficient data structures
   - Excessive object creation

### 3. **Optimization Strategies**

   **Algorithm Optimization:**
   - Replace inefficient algorithms
   - Use appropriate data structures
   - Implement caching where beneficial
   - Reduce computational complexity

   **Database Optimization:**
   - Add database indexes
   - Optimize queries (reduce joins, use projection)
   - Implement query caching
   - Use batch operations
   - Add read replicas if needed

   **Network Optimization:**
   - Reduce payload size (compression, pagination)
   - Implement HTTP caching
   - Use CDN for static assets
   - Minimize API calls (batching, debouncing)

   **Memory Optimization:**
   - Fix memory leaks
   - Use object pooling
   - Implement lazy loading
   - Optimize data structures

### 4. **Code-Level Optimizations**

   **JavaScript/TypeScript:**
   ```typescript
   // BEFORE (Inefficient)
   [Example of slow code]

   // AFTER (Optimized)
   [Example of optimized code]

   // PERFORMANCE GAIN: [X]x faster
   ```

   **Python:**
   ```python
   # BEFORE (Inefficient)
   [Example of slow code]

   # AFTER (Optimized)
   [Example of optimized code]

   # PERFORMANCE GAIN: [X]x faster
   ```

### 5. **Caching Strategy**

   **What to Cache:**
   - Frequently accessed data
   - Expensive computations
   - External API responses
   - Database query results

   **Caching Layers:**
   - In-memory cache (Redis, Memcached)
   - Application-level cache
   - Browser cache
   - CDN cache

   **Cache Invalidation:**
   - TTL-based expiration
   - Event-based invalidation
   - Manual cache clearing

### 6. **Async/Concurrency Optimization**

   **Parallelization:**
   - Identify independent operations
   - Use Promise.all() for parallel execution
   - Implement worker threads for CPU-intensive tasks

   **Example:**
   ```typescript
   // SEQUENTIAL (Slow)
   const result1 = await operation1();
   const result2 = await operation2();

   // PARALLEL (Fast)
   const [result1, result2] = await Promise.all([
     operation1(),
     operation2()
   ]);
   ```

### 7. **Database Query Optimization**

   **Query Analysis:**
   ```sql
   -- BEFORE (Slow)
   SELECT * FROM users WHERE email = 'user@example.com';

   -- AFTER (Fast - with index)
   CREATE INDEX idx_users_email ON users(email);
   SELECT id, name, email FROM users WHERE email = 'user@example.com';
   ```

   **N+1 Problem Fix:**
   ```typescript
   // BEFORE (N+1 queries)
   for (const user of users) {
     user.posts = await db.posts.find({ userId: user.id });
   }

   // AFTER (2 queries total)
   const userIds = users.map(u => u.id);
   const posts = await db.posts.find({ userId: { $in: userIds } });
   const postsByUser = groupBy(posts, 'userId');
   ```

### 8. **Monitoring & Measurement**

   **Metrics to Track:**
   - Response time (p50, p95, p99)
   - Throughput (requests/second)
   - Error rate
   - Resource utilization

   **Tools:**
   - Performance monitoring (APM)
   - Logging and tracing
   - Profiling tools
   - Load testing

### 9. **Benchmarking**

   **Before Optimization:**
   - Metric 1: [Baseline value]
   - Metric 2: [Baseline value]

   **After Optimization:**
   - Metric 1: [Improved value] ([X]% improvement)
   - Metric 2: [Improved value] ([X]% improvement)

   **Target Goals:**
   - Response time: < [X]ms
   - Throughput: > [X] req/s
   - Memory usage: < [X]MB

### 10. **Implementation Priority**

   **High Priority (Quick wins):**
   1. [Optimization 1]: [Expected impact]
   2. [Optimization 2]: [Expected impact]

   **Medium Priority:**
   1. [Optimization 1]: [Expected impact]
   2. [Optimization 2]: [Expected impact]

   **Low Priority (Nice to have):**
   1. [Optimization 1]: [Expected impact]

## Output Format

```
📊 PERFORMANCE ANALYSIS

Current Metrics:
- Response Time: [X]ms (p95)
- Throughput: [X] req/s
- Memory: [X]MB
- CPU: [X]%

🎯 BOTTLENECKS IDENTIFIED
1. [Bottleneck 1]
   - Location: [File:Line]
   - Impact: [High/Medium/Low]
   - Cause: [Root cause]

2. [Bottleneck 2]
   ...

🚀 OPTIMIZATION RECOMMENDATIONS

ALGORITHM OPTIMIZATIONS:
1. [Optimization 1]
   - Current: O([complexity])
   - Proposed: O([complexity])
   - Expected gain: [X]x faster

DATABASE OPTIMIZATIONS:
1. [Optimization 1]
   - Query: [Query]
   - Issue: [Problem]
   - Fix: [Solution]
   - Expected gain: [X]x faster

CACHING STRATEGY:
- Cache: [What to cache]
- Method: [Caching method]
- TTL: [Time to live]
- Expected gain: [X]x faster

CODE EXAMPLES:
[Before/After code comparisons]

📈 EXPECTED IMPROVEMENTS
- Response Time: [X]ms → [Y]ms ([Z]% faster)
- Throughput: [X] → [Y] req/s ([Z]% increase)
- Memory: [X]MB → [Y]MB ([Z]% reduction)

🎯 IMPLEMENTATION PLAN
High Priority:
- [ ] [Task 1]: [Expected impact]
- [ ] [Task 2]: [Expected impact]

Medium Priority:
- [ ] [Task 1]: [Expected impact]

📊 MONITORING SETUP
Metrics to track:
- [Metric 1]: Threshold [X]
- [Metric 2]: Threshold [Y]

Tools:
- [Tool 1]: [Purpose]
- [Tool 2]: [Purpose]
```

## Success Criteria

- ✅ Performance bottlenecks identified
- ✅ Optimization strategies defined
- ✅ Code examples provided
- ✅ Expected improvements quantified
- ✅ Implementation plan prioritized
- ✅ Monitoring strategy defined
- ✅ Measurable performance gains expected
