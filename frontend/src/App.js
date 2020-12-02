import React, { useState } from 'react';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import {Paper} from '@material-ui/core';
import {DropzoneArea} from 'material-ui-dropzone';
import { Button,
         CircularProgress,
         Table,
         TableBody,
         TableCell,
         TableHead,
         TableRow } from '@material-ui/core';
import { PictureAsPdf}  from '@material-ui/icons';
import download from 'downloadjs';


function App() {
  const [pdfFiles, setPdfFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [view, setView] = useState('input');
  const [csv, setCsv] = useState('');
  const [classificationDuration, setClassificationDuration] = useState(-1.0);
  const [requestDuration, setRequestDuration] = useState([-1.0]);

  const analyzeFiles = () => {
    const formData = new FormData();
    formData.append('num_files', pdfFiles.length);
    for(const pdfFile of pdfFiles) {
      formData.append(pdfFile.name, pdfFile);
    }

    const options = {
      method: 'POST',
      body: formData
    };

    console.log('Sending files for analysis');
    console.log(Array.from(formData.keys()));
    setView('loading');
    const t0 = new Date().getTime();
    //console.log(t0.getTime());
    //setRequestDuration(-1 * new Date().getTime()/1000.0);
    fetch('/analyze', options)
      .then((response) => response.json())
      .then((data) => {
        console.log('Got response:', data);
        setResults(data.results);
        setCsv(data.csv);
        setClassificationDuration(data.classification_duration);
        //console.log('t0', t0)
        //console.log('requestDuration', requestDuration);
        const duration = (new Date().getTime() - t0)/1000.0;
        console.log('duration', duration);
        setRequestDuration(duration); 
        setView('results');
      })
      .catch((error) => console.log('analyzeFiles() error:', error));
  };

  return (
    <Container maxWidth="sm">
      <Paper elevation={3}>
        {view === 'input' ?
          <Box my={4} p={2} textAlign="center" minHeight={400}>
           
            <Typography variant="h4" component="h1" gutterBottom>
              Allekirjoitusten tunnistaja
            </Typography>
            <DropzoneArea
              acceptedFiles={['application/pdf']}
              dropzoneText={'Tipauta PDF tähän tai napsauta kenttää'}
              getDropRejectMessage={(rejectedFile) => {
                return `Sovellus toimii pelkästään PDF-tiedostoilla. Tiedosto ${rejectedFile.name} ei kelpaa.`;
              }}
              Icon={PictureAsPdf}
              maxFileSize={100000000}
              onChange={(files) => {setPdfFiles(files)}}
              showFileNames={true}
              useChipsForPreview={true}
              
            />
            <Box my={2}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={analyzeFiles}>
                  Analysoi
              </Button>
            </Box>
          </Box>
        : null}

        {view === 'loading' ?
          <Box my={4} p={2} textAlign="center" minHeight={400}>
            <Typography variant="h4" component="h1" gutterBottom>
              Etsitään allekirjoituksia...
            </Typography>
            <Box my={12}>
              <CircularProgress />
            </Box>
          </Box>
        : null}

        {view === 'results' ?
          <Box my={4} p={2} textAlign="center" minHeight={400}>
            <Typography variant="h4" component="h1" gutterBottom>
              Tulokset
            </Typography>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Tiedosto</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Sivuja</TableCell>
                  <TableCell>Allekirjoituksia sivuilla</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.map((row) => (
                  <TableRow key={row.document}>
                    <TableCell component="th" scope="row">
                      {row.document}
                    </TableCell>
                    <TableCell>{row.status}</TableCell>
                    <TableCell>{row.num_pages}</TableCell>
                    <TableCell>{row.positive.length > 0 ? row.positive.join(", ") : 'Ei allekirjoituksia'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <Box my={2}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => {
                  setView('input')
                }}>
                  Takaisin
              </Button>
            </Box>
            <Box my={2}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => download(csv, 'results.csv', 'text/csv')}>
                  Tallenna CSV
              </Button>
            </Box>
            <Box>
              <Typography>Kokonaiskesto: {requestDuration.toFixed(1)} s</Typography>
              <Typography>Luokittelu: {classificationDuration.toFixed(1)} s</Typography>
              <Typography>Tiedonsiirto: {(requestDuration-classificationDuration).toFixed(1)} s</Typography>
            </Box>
            
          </Box>
        : null}
      </Paper>
    </Container>
  );
}

export default App;
