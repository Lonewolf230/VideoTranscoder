## Video Upload Pipeline


```mermaid
flowchart LR

subgraph Client
A[Select video]
B[Split into chunks]
C[Request upload session]
D[Upload chunks]
E[Collect ETags]
F[Complete upload request]
end

subgraph Backend
G[Create multipart upload]
H[Generate presigned URLs]
end

subgraph S3
I[Receive chunk uploads]
J[Assemble final video]
end

A --> B
B --> C
C --> G
G --> H
H --> D
D --> I
I --> E
E --> F
F --> J
```

This diagram illustrates the video upload pipeline, showcasing the interaction between the client, backend, and S3 storage. The client selects a video, splits it into chunks, and requests an upload session from the backend. The backend creates a multipart upload and generates presigned URLs for each chunk. The client then uploads the chunks directly to S3 using the presigned URLs. Once all chunks are uploaded, the client collects the ETags and sends a complete upload request to the backend, which instructs S3 to assemble the final video.

## Transcoding pipeline

```mermaid
flowchart LR

subgraph Client
A[Upload original video]
end

subgraph S3
B[Store original file]
end

subgraph Backend
C[Insert video record in DB]
D[Push job message to SQS]
end

subgraph Queue
E[SQS Queue]
end

subgraph Worker
F[Worker long polls queue]
G[Receive message]
H[Download video from S3]

subgraph Transcoding
I1[FFmpeg 720p]
I2[FFmpeg 480p]
end

subgraph Upload
J1[Upload 720p to S3]
J2[Upload 480p to S3]
end

K[Delete message from SQS]
end

subgraph S3_Output
L[Store processed videos]
end

A --> B
B --> C
C --> D
D --> E

E --> F
F --> G
G --> H

H --> I1
H --> I2

I1 --> J1
I2 --> J2

J1 --> L
J2 --> L

J1 --> K
J2 --> K
```

This diagram illustrates the video transcoding pipeline, showcasing the interaction between the client, S3 storage, backend, queue, worker, and output storage. The client uploads the original video to S3, which triggers the backend to insert a video record in the database and push a job message to an SQS queue. A worker long polls the queue, receives the message, and downloads the video from S3. The worker then transcodes the video into different resolutions (e.g., 720p and 480p) using FFmpeg. Finally, the transcoded videos are uploaded back to S3 for storage, and the corresponding messages are deleted from the SQS queue.