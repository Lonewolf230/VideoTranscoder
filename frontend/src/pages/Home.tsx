import axios from "axios";
import React, {useRef } from "react";

const base_url = "http://localhost:8000";

type Part={
    PartNumber: number;
    ETag: string;
}

export default function Home() {

    const upload_id = useRef<string | null>(null);
    const parts=useRef<Part[]>([])
    const vidfile = useRef<File | null>(null);
    const fileKey=useRef<string>("");

    const generateMultipartUpload = async () => {

        try {
            const res = await axios.post(base_url + "/create-multipart-upload");
            console.log("Multipart upload generated:", res.data);
            upload_id.current = res.data.upload_id;
            fileKey.current=res.data.file_key;
        }
        catch (err) {
            console.error("Error generating multipart upload:", err);
        }
    }

    const uploadVideo = async () => {
        const chunkSize = 10 * 1024 * 1024; // 5MB
        if (!vidfile.current) {
            console.error("No video file selected");
            return;
        }

        const file = vidfile.current;
        const totalParts = Math.ceil(file.size / chunkSize);

        try {
            //Generate presigned urls for all parts in one call
            console.log("Requesting presigned URLs for all parts...");
            const presignedUrlsRes = await axios.post(base_url + "/part-url", null, {
                params: {
                    upload_id: upload_id.current,
                    total_parts: totalParts,
                    file_key: fileKey.current
                }
            });
            console.log("Presigned URLs received:", presignedUrlsRes.data);
            const presignedUrls = presignedUrlsRes.data;
            
            await Promise.all(
                presignedUrls.map(async (part: { part_number: number; url: string })=>{
                    const partNumber=part.part_number;
                    const url=part.url;

                    const start = (partNumber - 1) * chunkSize;
                    const end = Math.min(start + chunkSize, file.size);
                    const chunk = file.slice(start, end);

                    const res = await axios.put(url, chunk, {
                        headers: {
                            "Content-Type": "application/octet-stream"
                        }
                    });

                    console.log(`Part ${partNumber} uploaded:`, res.headers.etag);

                    parts.current[partNumber-1]={
                        PartNumber: partNumber,
                        ETag: res.headers.etag
                    }
                })
            )

            console.log("All parts uploaded, completing multipart upload...");
            console.log(parts.current)
            await axios.post(base_url + "/complete-multipart-upload", {
                upload_id: upload_id.current,
                parts: parts.current,
                file_key: fileKey.current
            });
            console.log("Multipart upload completed successfully");
        }
        catch (err) {
            console.error("Error uploading video:", err);
        }
    }

    const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {

        const file = event?.target.files ? event.target.files[0] : null;
        if (file) {
            console.log("Selected file:", file.name);
            console.log("Selected file size:", file.size);
            vidfile.current = file;
        }
    }

    return (
        <>
            <button onClick={generateMultipartUpload}>Generate Multipart upload</button>

            <input type="file" onChange={onFileChange} accept=".mp4" />
            <button onClick={uploadVideo}>Upload Video</button>

        </>
    )
}